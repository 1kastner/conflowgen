import matplotlib.pyplot as plt


class UnitTestWithMatplotlib:
    def tearDown(self):  # pylint: disable=invalid-name
        plt.close("all")
