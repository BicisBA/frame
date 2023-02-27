from sklearn.metrics import confusion_matrix


def tn(y_true, y_pred):
    _tn, _, _, _ = confusion_matrix(
        y_true, y_pred, labels=[0, 1], normalize=None
    ).ravel()
    return _tn


def fp(y_true, y_pred):
    _, _fp, _, _ = confusion_matrix(
        y_true, y_pred, labels=[0, 1], normalize=None
    ).ravel()
    return _fp


def fn(y_true, y_pred):
    _, _, _fn, _ = confusion_matrix(
        y_true, y_pred, labels=[0, 1], normalize=None
    ).ravel()
    return _fn


def tp(y_true, y_pred):
    _, _, _, _tp = confusion_matrix(
        y_true, y_pred, labels=[0, 1], normalize=None
    ).ravel()
    return _tp
