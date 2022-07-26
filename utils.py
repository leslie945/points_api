from models import PointRecord

# generalized contains function
def list_contains(list, filter) -> PointRecord:
    for x in list:
        if filter(x):
            return x
    return None