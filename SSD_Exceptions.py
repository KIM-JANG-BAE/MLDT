class CapacityException(Exception):
    def __str__(self):
        return 'Capacity is too small. Enlarge Capacity.'