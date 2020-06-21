from typing import Set

from pypads import logger
from pypads.importext.mappings import MatchedMapping
from pypads.importext.wrapping.base_wrapper import BaseWrapper, Context


class ClassWrapper(BaseWrapper):

    def __init__(self, pypads):
        super().__init__(pypads)
        self._punched_class_names = set()

    @property
    def punched_class_names(self):
        return self._punched_class_names

    def wrap(self, clazz, context, matched_mappings: Set[MatchedMapping]):
        """
            Wrap a class in given ctx with pypads functionality
            :param clazz:
            :param context:
            :param matched_mappings:
            :return:
            """
        if clazz.__name__ not in self.punched_class_names:
            for matched_mapping in matched_mappings:
                try:
                    context.store_wrap_meta(matched_mapping, clazz)
                except Exception:
                    return clazz
            self.punched_class_names.add(clazz.__name__)

            if not context.has_original(clazz):
                context.store_original(clazz)

            # Module was changed and should be added to the list of modules which have been changed
            if hasattr(clazz, "__module__"):
                self._pypads.wrap_manager.module_wrapper.add_punched_module_name(clazz.__module__)

            attrs = {}
            for matched_mapping in matched_mappings:
                # Try to wrap every attr of the class
                for name in list(filter(
                        matched_mapping.mapping.applicable_filter(
                            Context(clazz, ".".join([context.reference, clazz.__name__]))),
                        dir(clazz))):
                    attr = getattr(clazz, name)
                    if attr not in attrs:
                        attrs[attr] = set()
                    else:
                        attrs[attr].add(matched_mapping)

            for attr, mm in attrs.items():
                self._pypads.wrap_manager.wrap(attr, clazz, mm)

            # Override class on module
            context.overwrite(clazz.__name__, clazz)
        else:
            logger.debug("Class " + str(clazz) + "already duck-puched.")
        return clazz
