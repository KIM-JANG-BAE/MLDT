class Page:
    '''
    Class about Page which include init, delete, write
    '''

    # initilize page class
    def __init__(self, page_id):
        self.page_id = page_id
        self.is_valid = False
    
    def write(self):
        self.is_valid = True


    def delete(self):
        self.is_valid = False