# Shared RScript port template

[中文](README.zh.md) | [English](README.en.md) | [Русский](README.ru.md)

[Project overview](../README.en.md) · [Full template guide (中文)](README.zh.md)

## UI resource map

Check these assets before implementing a new port. This is a shared checklist;
verify games with missing directories or different naming against their own resources.

| Path | Role |
| --- | --- |
| `grps/dt*` | Save-game images |
| `grps/nonbl/` | Number images used for menu pagination |
| `grps/compane/` | In-game control bar; image names identify button functions |
| `grps/confscrn/` | In-game right-click menu |
| `grps/savescrn/` | Save/load screen artwork |
| `.meta.xml` in each directory | Image positions and canvas layout; preserve original dimensions too |

Keep the original main menu. Its environment/settings button opens the existing
Text Settings screen (`rscript_title_preferences`); this does not replace the
whole main menu. In-game controls, the right-click menu and save/load screens
retain native artwork.

Read `.meta.xml` rather than guessing positions or centering every image.
Treat each save slot as a complete `saveconf` component: preview, numbers, date,
icons and selection mask. Do not replace the whole layout with a screenshot.
Wire each button to its own function and distinguish selected, idle and hover states.
