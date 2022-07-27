class CustomAssertions:
    def assertSamePointRecords(self, toTest, testWith):
        for index, item in enumerate(testWith):
            if item.__hash__() != toTest[index].__hash__():
                print(item.__hash__())
                print(toTest[index].__hash__())
                raise AssertionError('Not the same')
    

    def assertNotSamePointRecords(self, toTest, testWith):
        for index, item in enumerate(testWith):
            if item.__hash__() != toTest[index].__hash__():
                return

        raise AssertionError('Equal')