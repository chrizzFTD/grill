import types
import logging
import contextvars
from pathlib import Path
from functools import singledispatch

from grill import names

from pxr import UsdUtils, Usd, Sdf, Ar, Kind

logger = logging.getLogger(__name__)

repo = contextvars.ContextVar('repo')
DB_TOKENS = types.MappingProxyType(dict(kingdom="db", item='types'))


class UsdFile(names.CGAssetFile):
    DEFAULT_SUFFIX = 'usda'


from functools import lru_cache


@lru_cache(maxsize=None)
def fetch_stage(root_id) -> Usd.Stage:
    """For the given root layer identifier, get a corresponding stage.

    If layer does not exist, it is created in the repository.

    If a stage for the corresponding layer is found on the global cache, return it.
    Otherwise open it, populate the cache and return it.

    :param root_id:
    :return:
    """
    rootf = UsdFile(root_id)
    cache = UsdUtils.StageCache.Get()
    repo_path = repo.get()
    resolver_ctx = Ar.DefaultResolverContext([str(repo_path)])
    with Ar.ResolverContextBinder(resolver_ctx):
        layer_id = rootf.name
        logger.debug(f"Searching for {layer_id}")
        layer = Sdf.Layer.Find(layer_id)
        if not layer:
            logger.debug(f"Layer {layer_id} was not found open. Attempting to open it.")
            if not Sdf.Layer.FindOrOpen(layer_id):
                logger.debug(f"Layer {layer_id} does not exist on repository path: {resolver_ctx.GetSearchPath()}. Creating a new one.")
                # we first create a layer under our repo
                tmp_new_layer = Sdf.Layer.CreateNew(str(repo_path / layer_id))
                # delete it since it will have an identifier with the full path,
                # and we want to have the identifier relative to the repository path
                # TODO: with AR 2.0 it should be possible to create in memory layers
                #   with relative identifers to that of the search path of the context.
                #   In the meantime, we need to create the layer first on disk.
                del tmp_new_layer
            stage = Usd.Stage.Open(layer_id)
            logger.debug(f"Root layer: {stage.GetRootLayer()}")
            logger.debug(f"Opened stage: {stage}")
            cache_id = cache.Insert(stage)
            logger.debug(f"Added stage for {layer_id} with cache ID: {cache_id.ToString()}.")
        else:
            logger.debug(f"Layer was open. Found: {layer}")
            stage = cache.FindOneMatching(layer)
            if not stage:
                logger.debug(f"Could not find stage on the cache.")
                stage = Usd.Stage.Open(layer)
                cache_id = cache.Insert(stage)
                logger.debug(f"Added stage for {layer} with cache ID: {cache_id.ToString()}.")
            else:
                logger.debug(f"Found stage: {stage}")

    return stage


def define_db_type(stage, name, references=tuple()) -> Usd.Prim:
    db_root_path = Sdf.Path("/DBTypes")
    db_type_path = db_root_path.AppendChild(name)
    db_type = stage.GetPrimAtPath(db_type_path)
    if db_type:
        return db_type
    stage_layer = stage.GetRootLayer()
    current_asset_name = UsdFile(Path(stage.GetRootLayer().realPath).name)
    db_asset_name = current_asset_name.get(**DB_TOKENS)
    db_stage = fetch_stage(db_asset_name)

    db_layer = db_stage.GetRootLayer()
    if db_layer not in stage.GetLayerStack():
        # TODO: There's a slight chance that the identifier is not a relative one.
        #   Ensure we don't author absolute paths here. It should all be relative
        #   to a path in our search path from the current resolver context.
        #   If it's not happening, we need to manually create a relative asset path
        #   str(Path(db_layer.identifier).relative_to(repo))
        stage_layer.subLayerPaths.append(db_layer.identifier)

    # Use class prims since we want db types to be abstract.
    db_type = db_stage.CreateClassPrim(db_type_path)
    for reference in references:
        db_type.GetReferences().AddInternalReference(reference.GetPath())

    if not db_stage.GetDefaultPrim():
        db_stage.SetDefaultPrim(db_stage.GetPrimAtPath(db_root_path))
    return stage.GetPrimAtPath(db_type_path)


def _first_matching(tokens, layers):
    tokens = set(tokens.items())
    for layer in layers:
        name = UsdFile(Path(layer.realPath).name)
        if tokens.difference(name.values.items()):
            continue
        return layer
    raise ValueError(f"Could not find layer matching {tokens}")


def create(stage, dbtype, name, display_name=""):
    """Whenever we create a new item from the database, make it it's own entity"""
    new_tokens = dict(kingdom='assets', cluster=dbtype.GetName(), item=name)
    # contract: all dbtypes have a display_name
    current_asset_name = UsdFile(Path(stage.GetRootLayer().realPath).name)
    new_asset_name = current_asset_name.get(**new_tokens)

    # Scope collecting all assets of the same type
    scope_path = stage.GetPseudoRoot().GetPath().AppendPath(dbtype.GetName())
    scope = stage.GetPrimAtPath(scope_path)
    if not scope:
        scope = stage.DefinePrim(scope_path)
    if not scope.IsModel():
        Usd.ModelAPI(scope).SetKind(Kind.Tokens.assembly)
    path = scope_path.AppendChild(name)
    if stage.GetPrimAtPath(path):
        return stage.GetPrimAtPath(path)

    asset_stage = fetch_stage(new_asset_name)
    asset_origin = asset_stage.GetPrimAtPath("/origin")
    if not asset_origin:
        asset_origin = asset_stage.DefinePrim("/origin")
        db_layer = _first_matching(DB_TOKENS, stage.GetLayerStack())
        db_layer_relid = str(Path(db_layer.realPath).relative_to(repo.get()))
        asset_origin.GetReferences().AddReference(db_layer_relid, dbtype.GetPath())

    asset_stage.SetDefaultPrim(asset_origin)

    if display_name:
        asset_origin.GetAttribute("display_name").Set(display_name)

    over_prim = stage.OverridePrim(path)
    over_prim.GetPayloads().AddPayload(asset_stage.GetRootLayer().identifier)
    return over_prim


@singledispatch
def edit_context(obj, stage):
    raise ValueError(f"Not implemented: {locals()}")  # lazy


@edit_context.register
def _(obj: Sdf.Layer, stage):
    return Usd.EditContext(stage, obj)


@edit_context.register
def _(obj: Usd.Prim, layer, stage):
    # We need to explicitely construct our edit target since our layer is not on the layer stack of the stage.
    target = Usd.EditTarget(layer, obj.GetPrimIndex().rootNode.children[0])
    return Usd.EditContext(stage, target)
