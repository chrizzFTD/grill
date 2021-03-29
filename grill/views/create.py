from pxr import Usd
from PySide2 import QtWidgets, QtCore

from grill import write

from . import spreadsheet as _spreadsheet


# class _ColumnItemDelegate(QtWidgets.QStyledItemDelegate):
#     def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> QtWidgets.QWidget:
#         editor = QtWidgets.QComboBox(parent=parent)
#         editor.addItems(sorted(self.options))
#         return editor


class CreateAssets(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        form_l = QtWidgets.QFormLayout()
        layout = QtWidgets.QVBoxLayout()
        form = QtWidgets.QFrame()
        form.setLayout(form_l)
        form_l.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(form)
        self._amount = QtWidgets.QSpinBox()
        self._display_le = QtWidgets.QLineEdit()
        form_l.addRow('📚 Amount:', self._amount)
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        # self._type_delegate = _ColumnItemDelegate()
        self._asset_type_options = []

        #################### Move to own class?

        def _asset_type_combobox(parent, option, index):
            print("HELLO!!!!")
            combobox = QtWidgets.QComboBox(parent=parent)
            combobox.addItems(sorted(self._asset_type_options))
            return combobox

        options = _spreadsheet._ColumnOptions.NONE
        identity = lambda x: x
        _CREATE_ASSETS_COLUMNS = (
            _spreadsheet._Column("🧬 Type", identity, editor=_asset_type_combobox),
            _spreadsheet._Column("🔖 Asset Name", identity),
            _spreadsheet._Column("🏷 Display Name", identity),
            _spreadsheet._Column("📜 Description", identity),
        )

        self.table = table = _spreadsheet._Spreadsheet(_CREATE_ASSETS_COLUMNS, options)
        table.model.setHorizontalHeaderLabels([''] * len(_CREATE_ASSETS_COLUMNS))
        self._amount.valueChanged.connect(table.model.setRowCount)
        # table.table.setItemDelegateForColumn(0, self._type_delegate)
        table.layout().setContentsMargins(0, 0, 0, 0)
        ################

        self._amount.setValue(1)
        self._amount.setMinimum(1)
        self._amount.setMaximum(500)
        layout.addWidget(table)
        layout.addWidget(button_box)
        self.setLayout(layout)
        self.accepted.connect(self._create)
        self.setWindowTitle("Create Assets")
        size = table.table.viewportSizeHint()
        size.setWidth(size.width() + 60)
        size.setHeight(self.sizeHint().height())
        self.resize(size)

    @_spreadsheet.wait()
    def _create(self):
        types_root = self._stage.GetPrimAtPath("/DBTypes")
        model = self.table.table.model()
        for row in range(model.rowCount()):
            db_type_name = model.data(model.index(row, 0))
            db_type = types_root.GetPrimAtPath(db_type_name)
            asset_name = model.data(model.index(row, 1))
            if not asset_name:
                # TODO: validate and raise error dialog to user. For now we ignore.
                print(f"An asset name is required! Missing on row: {row}")
                continue
            display_name = model.data(model.index(row, 2))
            # print(locals())
            write.create(self._stage, db_type, asset_name, display_name)

    def setStage(self, stage):
        self._stage = stage
        types_root = stage.GetPrimAtPath("/DBTypes")
        self._asset_type_options = [child.GetName() for child in types_root.GetFilteredChildren(Usd.PrimIsAbstract)] if types_root else []
        # self._type_delegate.options = [child.GetName() for child in types_root.GetFilteredChildren(Usd.PrimIsAbstract)] if types_root else []
