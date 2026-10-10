# Bridge RScript permissions to native saves, autosaves and keyboard rollback.
init python:
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

    class FileSave(FileSave):
        def get_sensitive(self):
            return rscript_permission("save") and super().get_sensitive()

    def rscript_sync_permissions():
        if renpy.predicting():
            return
        rollback = rscript_permission("roll")
        if store._rollback != rollback:
            # Once the lock ends, scrolling must not re-enter the locked segment.
            renpy.block_rollback()
        store._rollback = rollback
        store._autosave = rscript_permission("save")
        # config.save also gates loading: restrict writes, not the save backend.

    config.interact_callbacks.append(rscript_sync_permissions)
