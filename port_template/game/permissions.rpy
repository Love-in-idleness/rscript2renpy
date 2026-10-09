# Bridge RScript permissions to native saves, autosaves and keyboard rollback.
init python:
    rscript_native_save_enabled = config.save

    def rscript_permission(kind):
        if not bool(getattr(store, kind + "_enabled")) or rscript_touch_locked():
            return False
        restricted = rscript_ui.get("restricted_image_folders", ())
        if restricted:
            scene = renpy.game.context().scene_lists
            for layer, image in store.layer_info.items():
                if (isinstance(image, str) and image.partition(" ")[0] in restricted
                        and store.layer_enabled.get(layer, 1)
                        and scene.get_displayable_by_tag(IMAGE_LAYER, "layer%d" % layer) is not None):
                    return False
        return True

    def rscript_sync_permissions():
        if renpy.predicting():
            return
        rollback = rscript_permission("roll")
        if store._rollback != rollback:
            # Once the lock ends, scrolling must not re-enter the locked segment.
            renpy.block_rollback()
        store._rollback = rollback
        store._autosave = rscript_permission("save")
        config.save = rscript_native_save_enabled and store._autosave

    config.interact_callbacks.append(rscript_sync_permissions)
