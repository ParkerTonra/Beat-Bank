from PyQt6.QtCore import QSortFilterProxyModel


class BeatFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_ids = []

    def set_filter_ids(self, ids):
        self.filter_ids = ids
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self.filter_ids:
            return True  # If no filter is set, show all rows
        model = self.sourceModel()
        track_id_index = model.index(source_row, 0, source_parent)  # Assuming track ID is in the first column
        track_id = model.data(track_id_index)
        print(f"Filtering row {source_row}: track ID {track_id}")
        return track_id in self.filter_ids