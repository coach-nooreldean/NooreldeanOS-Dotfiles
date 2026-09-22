import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: presentation
    anchors.fill: parent

    property int currentSlide: 0
    property int totalSlides: 4
    property int slideDuration: 8500

    Timer {
        id: slideTimer
        interval: presentation.slideDuration
        running: true
        repeat: true
        onTriggered: {
            presentation.currentSlide = (presentation.currentSlide + 1) % presentation.totalSlides
        }
    }

    // Deep modern dark background
    Rectangle {
        id: bg
        anchors.fill: parent
        color: "#0a0d14"

        // Subtle ambient radial glow that dynamically tints with the active slide
        Rectangle {
            id: ambientGlow
            width: 320
            height: 320
            radius: 160
            anchors.right: parent.right
            anchors.rightMargin: 40
            anchors.verticalCenter: parent.verticalCenter
            opacity: 0.12

            color: {
                switch(presentation.currentSlide) {
                    case 0: return "#00f2fe";
                    case 1: return "#c084fc";
                    case 2: return "#10b981";
                    case 3: return "#f59e0b";
                    default: return "#00f2fe";
                }
            }

            Behavior on color {
                ColorAnimation { duration: 600 }
            }
        }
    }

    // Slide Container
    Item {
        id: slideContainer
        anchors.fill: parent
        anchors.bottomMargin: 42

        // ====================================================================
        // SLIDE 1: Welcome & Arch Linux Base
        // ====================================================================
        Item {
            id: slide1
            anchors.fill: parent
            opacity: presentation.currentSlide === 0 ? 1.0 : 0.0
            visible: opacity > 0.01

            Behavior on opacity {
                NumberAnimation { duration: 450; easing.type: Easing.InOutQuad }
            }

            Column {
                anchors.left: parent.left
                anchors.leftMargin: 36
                anchors.verticalCenter: parent.verticalCenter
                width: parent.width - 240
                spacing: 8

                // Badge Pill
                Rectangle {
                    width: badgeText1.implicitWidth + 24
                    height: 24
                    radius: 12
                    color: "#111f30"
                    border.color: "#00f2fe"
                    border.width: 1

                    Row {
                        anchors.centerIn: parent
                        spacing: 6
                        Rectangle {
                            width: 6; height: 6; radius: 3; color: "#00f2fe"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Text {
                            id: badgeText1
                            text: "ARCH LINUX BASE"
                            color: "#00f2fe"
                            font.pixelSize: 10
                            font.bold: true
                            font.family: "JetBrains Mono, Noto Sans, monospace"
                        }
                    }
                }

                // Title
                Text {
                    text: "NooreldeanOS"
                    color: "#ffffff"
                    font.pixelSize: 26
                    font.bold: true
                    font.family: "JetBrains Mono, Noto Sans, sans-serif"
                }

                // Subtitle
                Text {
                    text: "Next-Generation Arch Linux Experience"
                    color: "#38bdf8"
                    font.pixelSize: 14
                    font.bold: true
                    font.family: "JetBrains Mono, Noto Sans, sans-serif"
                }

                // Arabic Description
                Text {
                    text: "مرحباً بك في NooreldeanOS — نظام تشغيل فائق السرعة مبني بعناية لرفع إنتاجيتك."
                    color: "#cbd5e1"
                    font.pixelSize: 13
                    font.family: "Noto Sans Arabic, Cairo, DejaVu Sans, sans-serif"
                    width: parent.width
                    wrapMode: Text.WordWrap
                    horizontalAlignment: Text.AlignLeft
                }

                Text {
                    text: "مزود بنواة linux-zen ونظام ملفات Btrfs مع ضغط Zstd لتجربة استثنائية سلسة."
                    color: "#94a3b8"
                    font.pixelSize: 12
                    font.family: "Noto Sans Arabic, Cairo, DejaVu Sans, sans-serif"
                    width: parent.width
                    wrapMode: Text.WordWrap
                    horizontalAlignment: Text.AlignLeft
                }

                Item { width: 1; height: 4 }

                // Feature Tags Grid
                Grid {
                    columns: 2
                    spacing: 8

                    Repeater {
                        model: ["linux-zen Kernel", "Zstd Compression", "ZRAM Enabled", "Btrfs Snapshots"]
                        Rectangle {
                            width: 170; height: 26; radius: 5
                            color: "#131b29"
                            border.color: "#1e293b"
                            border.width: 1

                            Row {
                                anchors.centerIn: parent
                                spacing: 6
                                Rectangle { width: 4; height: 4; radius: 2; color: "#38bdf8"; anchors.verticalCenter: parent.verticalCenter }
                                Text {
                                    text: modelData
                                    color: "#e2e8f0"
                                    font.pixelSize: 11
                                    font.family: "JetBrains Mono, monospace"
                                }
                            }
                        }
                    }
                }
            }

            // Right Visual: Logo Emblem
            Item {
                anchors.right: parent.right
                anchors.rightMargin: 48
                anchors.verticalCenter: parent.verticalCenter
                width: 120
                height: 120

                Image {
                    anchors.centerIn: parent
                    width: 100
                    height: 100
                    source: "logo.png"
                    fillMode: Image.PreserveAspectFit
                }
            }
        }

        // ====================================================================
        // SLIDE 2: Hyprland & Pywal Dynamic Colors
        // ====================================================================
        Item {
            id: slide2
            anchors.fill: parent
            opacity: presentation.currentSlide === 1 ? 1.0 : 0.0
            visible: opacity > 0.01

            Behavior on opacity {
                NumberAnimation { duration: 450; easing.type: Easing.InOutQuad }
            }

            Column {
                anchors.left: parent.left
                anchors.leftMargin: 36
                anchors.verticalCenter: parent.verticalCenter
                width: parent.width - 240
                spacing: 8

                Rectangle {
                    width: badgeText2.implicitWidth + 24
                    height: 24
                    radius: 12
                    color: "#21142e"
                    border.color: "#c084fc"
                    border.width: 1

                    Row {
                        anchors.centerIn: parent
                        spacing: 6
                        Rectangle {
                            width: 6; height: 6; radius: 3; color: "#c084fc"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Text {
                            id: badgeText2
                            text: "HYPRLAND & PYWAL"
                            color: "#c084fc"
                            font.pixelSize: 10
                            font.bold: true
                            font.family: "JetBrains Mono, Noto Sans, monospace"
                        }
                    }
                }

                Text {
                    text: "Dynamic Aesthetics"
                    color: "#ffffff"
                    font.pixelSize: 26
                    font.bold: true
                    font.family: "JetBrains Mono, Noto Sans, sans-serif"
                }

                Text {
                    text: "سحر الألوان التفاعلية وسلاسة Wayland"
                    color: "#f472b6"
                    font.pixelSize: 14
                    font.bold: true
                    font.family: "Noto Sans Arabic, Cairo, DejaVu Sans, sans-serif"
                }

                Text {
                    text: "محرك Pywal يقرأ ألوان أي خلفية تختارها ويولد نسقاً لونياً متناسقاً فورياً."
                    color: "#cbd5e1"
                    font.pixelSize: 13
                    font.family: "Noto Sans Arabic, Cairo, DejaVu Sans, sans-serif"
                    width: parent.width
                    wrapMode: Text.WordWrap
                    horizontalAlignment: Text.AlignLeft
                }

                Text {
                    text: "انسجام كامل بين النوافذ العائمة، الشريط العلوي، مركز الإشعارات، والطرفية."
                    color: "#94a3b8"
                    font.pixelSize: 12
                    font.family: "Noto Sans Arabic, Cairo, DejaVu Sans, sans-serif"
                    width: parent.width
                    wrapMode: Text.WordWrap
                    horizontalAlignment: Text.AlignLeft
                }

                Item { width: 1; height: 4 }

                Grid {
                    columns: 2
                    spacing: 8

                    Repeater {
                        model: ["Smooth Animations", "Catppuccin Accents", "30+ 4K Wallpapers", "Glassmorphism Blur"]
                        Rectangle {
                            width: 170; height: 26; radius: 5
                            color: "#1e1429"
                            border.color: "#3b1e54"
                            border.width: 1

                            Row {
                                anchors.centerIn: parent
                                spacing: 6
                                Rectangle { width: 4; height: 4; radius: 2; color: "#c084fc"; anchors.verticalCenter: parent.verticalCenter }
                                Text {
                                    text: modelData
                                    color: "#e2e8f0"
                                    font.pixelSize: 11
                                    font.family: "JetBrains Mono, monospace"
                                }
                            }
                        }
                    }
                }
            }

            // Right Visual: Color Palette Swatches
            Item {
                anchors.right: parent.right
                anchors.rightMargin: 44
                anchors.verticalCenter: parent.verticalCenter
                width: 130
                height: 120

                Grid {
                    anchors.centerIn: parent
                    columns: 4
                    spacing: 8

                    Repeater {
                        model: ["#ef4444", "#f97316", "#eab308", "#22c55e", "#06b6d4", "#3b82f6", "#a855f7", "#ec4899"]
                        Rectangle {
                            width: 24; height: 24; radius: 6
                            color: modelData
                            border.color: "#ffffff"
                            border.width: 1
                            opacity: 0.95
                        }
                    }
                }
            }
        }

        // ====================================================================
        // SLIDE 3: PipeWire Audio & SwayNC Notifications
        // ====================================================================
        Item {
            id: slide3
            anchors.fill: parent
            opacity: presentation.currentSlide === 2 ? 1.0 : 0.0
            visible: opacity > 0.01

            Behavior on opacity {
                NumberAnimation { duration: 450; easing.type: Easing.InOutQuad }
            }

            Column {
                anchors.left: parent.left
                anchors.leftMargin: 36
                anchors.verticalCenter: parent.verticalCenter
                width: parent.width - 240
                spacing: 8

                Rectangle {
                    width: badgeText3.implicitWidth + 24
                    height: 24
                    radius: 12
                    color: "#102820"
                    border.color: "#10b981"
                    border.width: 1

                    Row {
                        anchors.centerIn: parent
                        spacing: 6
                        Rectangle {
                            width: 6; height: 6; radius: 3; color: "#10b981"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Text {
                            id: badgeText3
                            text: "PIPEWIRE & SWAYNC"
                            color: "#10b981"
                            font.pixelSize: 10
                            font.bold: true
                            font.family: "JetBrains Mono, Noto Sans, monospace"
                        }
                    }
                }

                Text {
                    text: "Pro Audio & Controls"
                    color: "#ffffff"
                    font.pixelSize: 26
                    font.bold: true
                    font.family: "JetBrains Mono, Noto Sans, sans-serif"
                }

                Text {
                    text: "هندسة الصوت الاحترافية ومركز الإشعارات"
                    color: "#34d399"
                    font.pixelSize: 14
                    font.bold: true
                    font.family: "Noto Sans Arabic, Cairo, DejaVu Sans, sans-serif"
                }

                Text {
                    text: "تحكم فوري في مخارج الصوت وسماعات البلوتوث عبر اختصار Super + A."
                    color: "#cbd5e1"
                    font.pixelSize: 13
                    font.family: "Noto Sans Arabic, Cairo, DejaVu Sans, sans-serif"
                    width: parent.width
                    wrapMode: Text.WordWrap
                    horizontalAlignment: Text.AlignLeft
                }

                Text {
                    text: "مركز إشعارات SwayNC متطور مع سلايدرز الصوت والإضاءة ونغمات تنبيه هادئة."
                    color: "#94a3b8"
                    font.pixelSize: 12
                    font.family: "Noto Sans Arabic, Cairo, DejaVu Sans, sans-serif"
                    width: parent.width
                    wrapMode: Text.WordWrap
                    horizontalAlignment: Text.AlignLeft
                }

                Item { width: 1; height: 4 }

                Grid {
                    columns: 2
                    spacing: 8

                    Repeater {
                        model: ["Super + A Switcher", "6-Button Quick Grid", "PipeWire Low-Latency", "Audio Chimes"]
                        Rectangle {
                            width: 170; height: 26; radius: 5
                            color: "#0f231c"
                            border.color: "#1a4034"
                            border.width: 1

                            Row {
                                anchors.centerIn: parent
                                spacing: 6
                                Rectangle { width: 4; height: 4; radius: 2; color: "#34d399"; anchors.verticalCenter: parent.verticalCenter }
                                Text {
                                    text: modelData
                                    color: "#e2e8f0"
                                    font.pixelSize: 11
                                    font.family: "JetBrains Mono, monospace"
                                }
                            }
                        }
                    }
                }
            }

            // Right Visual: Audio Equalizer Bars
            Item {
                anchors.right: parent.right
                anchors.rightMargin: 48
                anchors.verticalCenter: parent.verticalCenter
                width: 120
                height: 100

                Row {
                    anchors.centerIn: parent
                    spacing: 5

                    Repeater {
                        model: [16, 28, 48, 22, 42, 58, 36, 52, 24, 38, 18]
                        Rectangle {
                            width: 5
                            height: modelData
                            radius: 3
                            color: "#34d399"
                            anchors.verticalCenter: parent.verticalCenter
                            opacity: 0.85
                        }
                    }
                }
            }
        }

        // ====================================================================
        // SLIDE 4: Developer & Productivity Tools
        // ====================================================================
        Item {
            id: slide4
            anchors.fill: parent
            opacity: presentation.currentSlide === 3 ? 1.0 : 0.0
            visible: opacity > 0.01

            Behavior on opacity {
                NumberAnimation { duration: 450; easing.type: Easing.InOutQuad }
            }

            Column {
                anchors.left: parent.left
                anchors.leftMargin: 36
                anchors.verticalCenter: parent.verticalCenter
                width: parent.width - 240
                spacing: 8

                Rectangle {
                    width: badgeText4.implicitWidth + 24
                    height: 24
                    radius: 12
                    color: "#291d0f"
                    border.color: "#f59e0b"
                    border.width: 1

                    Row {
                        anchors.centerIn: parent
                        spacing: 6
                        Rectangle {
                            width: 6; height: 6; radius: 3; color: "#f59e0b"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Text {
                            id: badgeText4
                            text: "DEVELOPER WORKFLOW"
                            color: "#f59e0b"
                            font.pixelSize: 10
                            font.bold: true
                            font.family: "JetBrains Mono, Noto Sans, monospace"
                        }
                    }
                }

                Text {
                    text: "Peak Productivity"
                    color: "#ffffff"
                    font.pixelSize: 26
                    font.bold: true
                    font.family: "JetBrains Mono, Noto Sans, sans-serif"
                }

                Text {
                    text: "أقصى كفاءة للمطورين وصناع المحتوى"
                    color: "#fbbf24"
                    font.pixelSize: 14
                    font.bold: true
                    font.family: "Noto Sans Arabic, Cairo, DejaVu Sans, sans-serif"
                }

                Text {
                    text: "طرفية Kitty فائقة السرعة مع برومبت Starship الذكي وأداة Yazi لإدارة الملفات."
                    color: "#cbd5e1"
                    font.pixelSize: 13
                    font.family: "Noto Sans Arabic, Cairo, DejaVu Sans, sans-serif"
                    width: parent.width
                    wrapMode: Text.WordWrap
                    horizontalAlignment: Text.AlignLeft
                }

                Text {
                    text: "أداة sys-clean لصيانة الكاش التلقائية وحذف الحزم المهملة بضغطة زر."
                    color: "#94a3b8"
                    font.pixelSize: 12
                    font.family: "Noto Sans Arabic, Cairo, DejaVu Sans, sans-serif"
                    width: parent.width
                    wrapMode: Text.WordWrap
                    horizontalAlignment: Text.AlignLeft
                }

                Item { width: 1; height: 4 }

                Grid {
                    columns: 2
                    spacing: 8

                    Repeater {
                        model: ["Super + Return Kitty", "Super + R Rofi Run", "sys-clean Optimizer", "Git & Fastfetch"]
                        Rectangle {
                            width: 170; height: 26; radius: 5
                            color: "#24190c"
                            border.color: "#3d2b14"
                            border.width: 1

                            Row {
                                anchors.centerIn: parent
                                spacing: 6
                                Rectangle { width: 4; height: 4; radius: 2; color: "#fbbf24"; anchors.verticalCenter: parent.verticalCenter }
                                Text {
                                    text: modelData
                                    color: "#e2e8f0"
                                    font.pixelSize: 11
                                    font.family: "JetBrains Mono, monospace"
                                }
                            }
                        }
                    }
                }
            }

            // Right Visual: Mini Terminal Card
            Rectangle {
                anchors.right: parent.right
                anchors.rightMargin: 36
                anchors.verticalCenter: parent.verticalCenter
                width: 140
                height: 90
                radius: 8
                color: "#0f172a"
                border.color: "#f59e0b"
                border.width: 1

                Row {
                    anchors.top: parent.top
                    anchors.topMargin: 8
                    anchors.left: parent.left
                    anchors.leftMargin: 8
                    spacing: 4

                    Rectangle { width: 7; height: 7; radius: 4; color: "#ef4444" }
                    Rectangle { width: 7; height: 7; radius: 4; color: "#f59e0b" }
                    Rectangle { width: 7; height: 7; radius: 4; color: "#22c55e" }
                }

                Column {
                    anchors.centerIn: parent
                    anchors.verticalCenterOffset: 6
                    spacing: 4

                    Text {
                        text: "➜ sys-clean"
                        color: "#38bdf8"
                        font.pixelSize: 10
                        font.family: "JetBrains Mono, monospace"
                    }
                    Text {
                        text: "[✔] Optimized"
                        color: "#4ade80"
                        font.pixelSize: 10
                        font.bold: true
                        font.family: "JetBrains Mono, monospace"
                    }
                }
            }
        }
    }

    // Interactive Animated Navigation Indicator Dots
    Row {
        id: dotsRow
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 14
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 10

        Repeater {
            model: presentation.totalSlides
            Rectangle {
                width: index === presentation.currentSlide ? 24 : 8
                height: 8
                radius: 4
                color: index === presentation.currentSlide ? "#00f2fe" : "#334155"

                Behavior on width {
                    NumberAnimation { duration: 250; easing.type: Easing.OutCubic }
                }
                Behavior on color {
                    ColorAnimation { duration: 250 }
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
