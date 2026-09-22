import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: presentation
    anchors.fill: parent

    property int currentSlide: 0
    property int totalSlides: 4
    property int slideDuration: 8000

    Timer {
        id: slideTimer
        interval: presentation.slideDuration
        running: true
        repeat: true
        onTriggered: {
            presentation.currentSlide = (presentation.currentSlide + 1) % presentation.totalSlides
        }
    }

    Rectangle {
        id: background
        anchors.fill: parent
        color: "#0a0c13"
    }

    // Slide Container
    Item {
        id: slideContainer
        anchors.fill: parent
        anchors.bottomMargin: 50

        // Slide 1: Welcome & Arch Linux Base
        Image {
            id: slide1
            anchors.centerIn: parent
            width: Math.min(parent.width - 40, 680)
            height: Math.min(parent.height - 20, 320)
            fillMode: Image.PreserveAspectFit
            source: "slide1_welcome.png"
            opacity: presentation.currentSlide === 0 ? 1.0 : 0.0
            visible: opacity > 0.01

            Behavior on opacity {
                NumberAnimation { duration: 600; easing.type: Easing.InOutQuad }
            }
        }

        // Slide 2: Hyprland & Pywal Dynamic Colors
        Image {
            id: slide2
            anchors.centerIn: parent
            width: Math.min(parent.width - 40, 680)
            height: Math.min(parent.height - 20, 320)
            fillMode: Image.PreserveAspectFit
            source: "slide2_hyprland.png"
            opacity: presentation.currentSlide === 1 ? 1.0 : 0.0
            visible: opacity > 0.01

            Behavior on opacity {
                NumberAnimation { duration: 600; easing.type: Easing.InOutQuad }
            }
        }

        // Slide 3: PipeWire Audio & SwayNC Notifications
        Image {
            id: slide3
            anchors.centerIn: parent
            width: Math.min(parent.width - 40, 680)
            height: Math.min(parent.height - 20, 320)
            fillMode: Image.PreserveAspectFit
            source: "slide3_audio.png"
            opacity: presentation.currentSlide === 2 ? 1.0 : 0.0
            visible: opacity > 0.01

            Behavior on opacity {
                NumberAnimation { duration: 600; easing.type: Easing.InOutQuad }
            }
        }

        // Slide 4: Developer & Productivity Tools
        Image {
            id: slide4
            anchors.centerIn: parent
            width: Math.min(parent.width - 40, 680)
            height: Math.min(parent.height - 20, 320)
            fillMode: Image.PreserveAspectFit
            source: "slide4_dev.png"
            opacity: presentation.currentSlide === 3 ? 1.0 : 0.0
            visible: opacity > 0.01

            Behavior on opacity {
                NumberAnimation { duration: 600; easing.type: Easing.InOutQuad }
            }
        }
    }

    // Interactive Navigation Indicator Dots
    Row {
        id: dotsRow
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 18
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 12

        Repeater {
            model: presentation.totalSlides
            Rectangle {
                width: index === presentation.currentSlide ? 28 : 10
                height: 10
                radius: 5
                color: index === presentation.currentSlide ? "#00f2fe" : "#334155"

                Behavior on width {
                    NumberAnimation { duration: 300; easing.type: Easing.OutCubic }
                }
                Behavior on color {
                    ColorAnimation { duration: 300 }
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        presentation.currentSlide = index
                        slideTimer.restart()
                    }
                }
            }
        }
    }
}
