-- NooreldeanOS Hyprland Configuration
-- Refer to the wiki for more information.
-- https://wiki.hypr.land/Configuring/Start/

local colors = require("colors")



------------------
---- MONITORS ----
------------------

-- See https://wiki.hypr.land/Configuring/Basics/Monitors/
hl.monitor({
    output   = "",
    mode     = "preferred",
    position = "auto",
    scale    = "auto",
})


---------------------
---- MY PROGRAMS ----
---------------------

-- Set programs that you use
local terminal    = "kitty"
local fileManager = "kitty -e yazi"
local menu = "rofi -show drun"


-------------------
---- AUTOSTART ----
-------------------

-- See https://wiki.hypr.land/Configuring/Basics/Autostart/

-- Autostart necessary processes (like notifications daemons, status bars, etc.)
-- Or execute your favorite apps at launch like this:
--
hl.on("hyprland.start", function ()
    hl.exec_cmd("/usr/lib/polkit-kde-authentication-agent-1")
    hl.exec_cmd("dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP QT_QPA_PLATFORMTHEME QT_STYLE_OVERRIDE")
    hl.exec_cmd("awww-daemon &")
    hl.exec_cmd("copyq --start-server &")
    hl.exec_cmd("waybar &")
    hl.exec_cmd("~/.config/hypr/scripts/startup_wallpaper.sh &")
    hl.exec_cmd("udiskie &")
    hl.exec_cmd("swaync &")
    hl.exec_cmd("swayosd-server &")
    hl.exec_cmd("xsettingsd &")
    hl.exec_cmd("nm-applet &")
    hl.exec_cmd("blueman-applet &")
end)


-------------------------------
---- ENVIRONMENT VARIABLES ----
-------------------------------

-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Environment-variables/

hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")
-- hl.env("XCURSOR_THEME", "Layan-cursors")
hl.env("QT_QPA_PLATFORMTHEME", "qt5ct")
hl.env("QT_STYLE_OVERRIDE", "kvantum")

-----------------------
----- PERMISSIONS -----
-----------------------

-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Permissions/
-- Please note permission changes here require a Hyprland restart and are not applied on-the-fly
-- for security reasons

-- hl.config({
--   ecosystem = {
--     enforce_permissions = true,
--   },
-- })

-- hl.permission("/usr/(bin|local/bin)/grim", "screencopy", "allow")
-- hl.permission("/usr/(lib|libexec|lib64)/xdg-desktop-portal-hyprland", "screencopy", "allow")
-- hl.permission("/usr/(bin|local/bin)/hyprpm", "plugin", "allow")


-----------------------
---- LOOK AND FEEL ----
-----------------------

-- Refer to https://wiki.hypr.land/Configuring/Basics/Variables/
hl.config({
    general = {
    gaps_in  = 5,
    gaps_out = 15,

    border_size = 4,

  col = {
    active_border = colors.color4,
    inactive_border = colors.color0,
  },

    resize_on_border = true,

    allow_tearing = false,

    layout = "dwindle",
},

    decoration = {
    rounding       = 16,
    rounding_power = 3,

    active_opacity   = 0.95,
    inactive_opacity = 0.85,

    shadow = {
        enabled      = true,
        range        = 40,
        render_power = 4,
        color        = "rgba(00000088)",
    },

    blur = {
        enabled   = true,
        size      = 12,
        passes    = 4,
        vibrancy  = 0.8,
        ignore_opacity = true,
        new_optimizations = true,
        xray      = false,
    },
},

    animations = {
        enabled = true,
    },
})

-- Default curves and animations, see https://wiki.hypr.land/Configuring/Advanced-and-Cool/Animations/
-- Smooth macOS-like animations
hl.curve("overshot", { type = "bezier", points = { {0.05, 0.9}, {0.1, 1.1} } })
hl.curve("smoothOut", { type = "bezier", points = { {0.36, 0}, {0.66, -0.56} } })
hl.curve("smoothIn", { type = "bezier", points = { {0.25, 1}, {0.5, 1} } })
hl.curve("linear", { type = "bezier", points = { {0.0, 0.0}, {1.0, 1.0} } })
hl.curve("spring", { type = "bezier", points = { {0.4, 0.0}, {0.2, 1.15} } })

hl.animation({ leaf = "windows",       enabled = true,  speed = 6,  bezier = "overshot", style = "slide" })
hl.animation({ leaf = "windowsOut",    enabled = true,  speed = 5,  bezier = "smoothOut", style = "slide" })
hl.animation({ leaf = "windowsMove",   enabled = true,  speed = 5,  bezier = "overshot", style = "slide" })
hl.animation({ leaf = "layers",        enabled = true,  speed = 5,  bezier = "overshot", style = "popin 80%" })
hl.animation({ leaf = "border",        enabled = true,  speed = 10, bezier = "default" })
hl.animation({ leaf = "borderangle",   enabled = true,  speed = 100, bezier = "linear", style = "loop" })
hl.animation({ leaf = "fade",          enabled = true,  speed = 5,  bezier = "smoothIn" })
hl.animation({ leaf = "workspaces",    enabled = true,  speed = 7,  bezier = "overshot", style = "slide" })


-- Ref https://wiki.hypr.land/Configuring/Basics/Workspace-Rules/
-- "Smart gaps" / "No gaps when only"
-- uncomment all if you wish to use that.
-- hl.workspace_rule({ workspace = "w[tv1]", gaps_out = 0, gaps_in = 0 })
-- hl.workspace_rule({ workspace = "f[1]",   gaps_out = 0, gaps_in = 0 })
-- hl.window_rule({
--     name  = "no-gaps-wtv1",
--     match = { float = false, workspace = "w[tv1]" },
--     border_size = 0,
--     rounding    = 0,
-- })
-- hl.window_rule({
--     name  = "no-gaps-f1",
--     match = { float = false, workspace = "f[1]" },
--     border_size = 0,
--     rounding    = 0,
-- })
hl.window_rule({
    name  = "move-hyprland-run",
    match = { class = "hyprland-run" },

    move  = "20 monitor_h-120",
    float = true,
})
hl.window_rule({
    name = "calculator",

    match = {
        class = "org.gnome.Calculator",
    },

    float = true,
    center = true,
})


hl.window_rule({
    name = "wlogout-float",
    match = { class = "wlogout" },
    float = true,
    fullscreen = true,
})
hl.window_rule({
    name = "swaync-float",
    match = { class = "Swaync" },
    float = true,
})
hl.window_rule({
    name = "opacity-rules",
    match = { class = ".*" },
    opacity = "0.85 0.7", -- Active 0.85, Inactive 0.7
})
-- Exclude certain apps from opacity
hl.window_rule({
    name = "opacity-exclude-video",
    match = { class = "vlc|mpv|youtube|browser" },
    opacity = "1.0 1.0",
})

-- See https://wiki.hypr.land/Configuring/Layouts/Dwindle-Layout/ for more
hl.config({
    dwindle = {
        preserve_split = true, -- You probably want this
    },
})

-- See https://wiki.hypr.land/Configuring/Layouts/Master-Layout/ for more
hl.config({
    master = {
        new_status = "master",
    },
})

-- See https://wiki.hypr.land/Configuring/Layouts/Scrolling-Layout/ for more
hl.config({
    scrolling = {
        fullscreen_on_one_column = true,
    },
})

----------------
----  MISC  ----
----------------

hl.config({
    misc = {
        force_default_wallpaper = 0,    -- Set to 0 or 1 to disable the anime mascot wallpapers
        disable_hyprland_logo   = true, -- If true disables the random hyprland logo / anime girl background. :(
    },
})


---------------
---- INPUT ----
---------------

hl.config({
    input = {
        kb_layout  = "us,ara",
        kb_variant = ",",
        kb_model   = "",
        kb_options = "grp:alt_shift_toggle",
        kb_rules   = "",

        follow_mouse = 1,

        sensitivity = 0, -- -1.0 - 1.0, 0 means no modification.

        touchpad = {
            natural_scroll = true,
            tap_to_click = true,
            clickfinger_behavior = true,
        },
    },
})

hl.gesture({
    fingers = 3,
    direction = "horizontal",
    action = "workspace"
})

-- Example per-device config
-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Devices/ for more
hl.device({
    name        = "epic-mouse-v1",
    sensitivity = -0.5,
})


---------------------
---- KEYBINDINGS ----
---------------------

local mainMod = "SUPER" -- Sets "Windows" key as main modifier

-- Example binds, see https://wiki.hypr.land/Configuring/Basics/Binds/ for more
hl.bind(mainMod .. " + Return", hl.dsp.exec_cmd(terminal))
hl.bind(mainMod .. " + Q", hl.dsp.window.close())
hl.bind(mainMod .. " + L", hl.dsp.exec_cmd("hyprlock"))
hl.bind(mainMod .. " + N", hl.dsp.exec_cmd("swaync-client -t"))
hl.bind(mainMod .. " + SHIFT + B",
    hl.dsp.exec_cmd("pkill waybar && waybar &"))
-- closeWindowBind:set_enabled(false)
hl.bind(mainMod .. " + M", hl.dsp.exec_cmd("command -v hyprshutdown >/dev/null 2>&1 && hyprshutdown || hyprctl dispatch exit"))
hl.bind(mainMod .. " + E", hl.dsp.exec_cmd(fileManager))
hl.bind(mainMod .. " + F", hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + R", hl.dsp.exec_cmd(menu))
hl.bind(mainMod .. " + P", hl.dsp.window.pseudo())
hl.bind(mainMod .. " + J", hl.dsp.layout("togglesplit"))    -- dwindle only
hl.bind(mainMod .. " + ESCAPE",
    hl.dsp.exec_cmd("wlogout"))
-- Move focus with mainMod + arrow keys
hl.bind(mainMod .. " + left",  hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + right", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + up",    hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + down",  hl.dsp.focus({ direction = "down" }))
hl.bind(mainMod .. " + V", hl.dsp.exec_cmd("copyq toggle"))
hl.bind(mainMod .. " + B", hl.dsp.exec_cmd("google-chrome-stable"))
-- Switch workspaces with mainMod + [0-9]
-- Move active window to a workspace with mainMod + SHIFT + [0-9]
for i = 1, 10 do
    local key = i % 10 -- 10 maps to key 0
    hl.bind(mainMod .. " + " .. key,             hl.dsp.focus({ workspace = i}))
    hl.bind(mainMod .. " + SHIFT + " .. key,     hl.dsp.window.move({ workspace = i }))
end

-- Example special workspace (scratchpad)
hl.bind(mainMod .. " + Z",         hl.dsp.workspace.toggle_special("magic"))
hl.bind(mainMod .. " + SHIFT + Z", hl.dsp.window.move({ workspace = "special:magic" }))

-- Scroll through existing workspaces with mainMod + scroll
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up",   hl.dsp.focus({ workspace = "e-1" }))

-- Move/resize windows with mainMod + LMB/RMB and dragging
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(),   { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- Laptop multimedia keys for volume and LCD brightness
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("swayosd-client --output-volume raise"), { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("swayosd-client --output-volume lower"), { locked = true, repeating = true })
hl.bind("XF86AudioMute",        hl.dsp.exec_cmd("swayosd-client --output-volume mute-toggle"), { locked = true, repeating = true })
hl.bind("XF86AudioMicMute",     hl.dsp.exec_cmd("swayosd-client --input-volume mute-toggle"),   { locked = true, repeating = true })
hl.bind("XF86MonBrightnessUp",  hl.dsp.exec_cmd("swayosd-client --brightness raise"), { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown",hl.dsp.exec_cmd("swayosd-client --brightness lower"), { locked = true, repeating = true })

-- Requires playerctl
hl.bind("XF86AudioNext",  hl.dsp.exec_cmd("playerctl next"),       { locked = true })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPlay",  hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPrev",  hl.dsp.exec_cmd("playerctl previous"),   { locked = true })
-- تصوير منطقة معينة (Super + S)
hl.bind(mainMod .. " + S", hl.dsp.exec_cmd("~/.config/hypr/scripts/screenshot.sh region"))
-- تصوير الشاشة كاملة (Print Screen)
hl.bind("Print", hl.dsp.exec_cmd("~/.config/hypr/scripts/screenshot.sh output"))

-- New Useful Shortcuts added by Antigravity
hl.bind(mainMod .. " + SHIFT + F", hl.dsp.window.fullscreen())
hl.bind(mainMod .. " + ALT + W", hl.dsp.exec_cmd("killall -SIGUSR1 waybar"))
hl.bind(mainMod .. " + T", hl.dsp.exec_cmd("telegram-desktop"))
hl.bind(mainMod .. " + C", hl.dsp.exec_cmd("antigravity-ide"))
hl.bind(mainMod .. " + SHIFT + C", hl.dsp.exec_cmd("hyprpicker -a -n"))


--------------------------------
---- WINDOWS AND WORKSPACES ----
--------------------------------

-- See https://wiki.hypr.land/Configuring/Basics/Window-Rules/
-- and https://wiki.hypr.land/Configuring/Basics/Workspace-Rules/

-- Example window rules that are useful

hl.window_rule({ name = "blueman-float", match = { class = "blueman-manager" }, float = true, center = true })
hl.window_rule({ name = "nm-float", match = { class = "nm-connection-editor" }, float = true, center = true })

local suppressMaximizeRule = hl.window_rule({
    -- Ignore maximize requests from all apps. You'll probably like this.
    name  = "suppress-maximize-events",
    match = { class = ".*" },

    suppress_event = "maximize",
})
-- suppressMaximizeRule:set_enabled(false)

hl.window_rule({
    -- Fix some dragging issues with XWayland
    name  = "fix-xwayland-drags",
    match = {
        class      = "^$",
        title      = "^$",
        xwayland   = true,
        float      = true,
        fullscreen = false,
        pin        = false,
    },

    no_focus = true,
})

-- Layer rules also return a handle.
-- local overlayLayerRule = hl.layer_rule({
--     name  = "no-anim-overlay",
--     match = { namespace = "^my-overlay$" },
--     no_anim = true,
-- })
-- overlayLayerRule:set_enabled(false)

-- Blur for Waybar, SwayNC, and Wlogout
hl.layer_rule({ name = "waybar-blur", match = { namespace = "waybar" }, blur = true, ignore_alpha = 0.2 })
hl.layer_rule({ name = "swaync-blur", match = { namespace = "swaync-control-center" }, blur = true, ignore_alpha = 0.2 })
hl.layer_rule({ name = "wlogout-blur", match = { namespace = "wlogout" }, blur = true, ignore_alpha = 0.5 })
hl.layer_rule({ name = "rofi-blur", match = { namespace = "rofi" }, blur = true, ignore_alpha = 0.2 })

-- Dimming effects
hl.layer_rule({ name = "rofi-dim", match = { namespace = "rofi" }, dim_around = true })
hl.layer_rule({ name = "swaync-dim", match = { namespace = "swaync-control-center" }, dim_around = true })



hl.window_rule({
    name  = "pavucontrol-float",
    match = { class = "^pavucontrol$" },
    float = true,
    size = "800 500",
    center = true,
})


