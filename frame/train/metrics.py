from sklearn.metrics import confusion_matrix


def tn(y_true, y_pred, normalize="all"):
    _tn, _, _, _ = confusion_matrix(
        y_true, y_pred, labels=[0, 1], normalize=normalize
    ).ravel()
    return _tn


def fp(y_true, y_pred, normalize="all"):
    _, _fp, _, _ = confusion_matrix(
        y_true, y_pred, labels=[0, 1], normalize=normalize
    ).ravel()
    return _fp


def fn(y_true, y_pred, normalize="all"):
    _, _, _fn, _ = confusion_matrix(
        y_true, y_pred, labels=[0, 1], normalize=normalize
    ).ravel()
    return _fn


def tp(y_true, y_pred, normalize="all"):
    _, _, _, _tp = confusion_matrix(
        y_true, y_pred, labels=[0, 1], normalize=normalize
    ).ravel()
    return _tp
