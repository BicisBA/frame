import pandas as pd
from sklearn.metrics import confusion_matrix


def false_positives(y_true, y_pred):
    _, fp, _, _ = confusion_matrix(
        y_true, y_pred, labels=[1, 0], normalize="true"
    ).ravel()
    return fp


def cm_json(y_true, y_pred):
    conf_matrix = confusion_matrix(y_true, y_pred, labels=[1, 0])
    conf_matrix = pd.DataFrame(conf_matrix, columns=[False, True], index=[False, True])
    return conf_matrix.to_json()
