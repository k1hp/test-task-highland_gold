import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget


def main():
    # You need one (and only one) QApplication instance per application.
    # Pass in sys.argv to allow command line arguments for your app.
    # If you know you won't use command line arguments QApplication([]) works too.
    app = QApplication(sys.argv)

    # Create a Qt widget, which will be our window.
    window = QWidget()
    window.setWindowTitle("Hello PyQt5")  # Set the window title
    window.setGeometry(
        100, 100, 400, 200
    )  # Set window position and size (x, y, width, height)

    # Add a label to the window
    label = QLabel("Hello World!", parent=window)
    label.move(150, 90)  # Move label to the center of the window

    # Show the window
    window.show()

    # Start the event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
