# Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/CompoundElement.py
from __future__ import with_statement
from itertools import ifilter
from SubjectSlot import subject_slot_group, SlotManager
from NotifyingControlElement import NotifyingControlElement
from Util import BooleanContext, first, second

class CompoundElement(NotifyingControlElement, SlotManager):
    """
    Utility class that helps in writing Elements that act as a facade
    to nested elements, hiding the complexity oif making sure that
    resource ownership rules are preserved.
    """
    _is_resource_based = False

    def __init__(self, *a, **k):
        super(CompoundElement, self).__init__(*a, **k)
        self._nested_control_elements = dict()
        self._disable_notify_owner_on_button_ownership_change = BooleanContext()
        self._listen_nested_requests = 0

    def on_nested_control_element_grabbed(self, control):
        """
        Notifies that the nested control can be used by the compound
        """
        raise NotImplementedError

    def on_nested_control_element_released(self, control):
        """
        Notifies that we lost control over the control.
        """
        raise NotImplementedError

    def on_nested_control_element_value(self, control, value):
        """
        Notifies that an owned control element has received a value.
        """
        raise NotImplementedError

    def get_control_element_priority(self, element):
        """
        Override to change priority for control element.
        """
        raise self._has_resource or AssertionError
        return self.resource.max_priority

    def register_control_elements(self, *elements):
        return map(self.register_control_element, elements)

    def register_control_element(self, element):
        if not element not in self._nested_control_elements:
            raise AssertionError
            self._nested_control_elements[element] = False
            if self._listen_nested_requests > 0:
                self._on_nested_control_element_value.add_subject(element)
            priority = self._is_resource_based and self.resource.owner and self.get_control_element_priority(element)
            element.resource.grab(self, priority=priority)
        elif not self._is_resource_based:
            with self._disable_notify_owner_on_button_ownership_change():
                element.notify_ownership_change(self, True)
        return element

    def unregister_control_elements(self, *elements):
        return map(self.unregister_control_element, elements)

    def unregister_control_element(self, element):
        if not element in self._nested_control_elements:
            raise AssertionError
            if self._is_resource_based and self.resource.owner:
                element.resource.release(self)
            elif not self._is_resource_based:
                with self._disable_notify_owner_on_button_ownership_change():
                    element.notify_ownership_change(self, False)
            self._listen_nested_requests > 0 and self._on_nested_control_element_value.remove_subject(element)
        del self._nested_control_elements[element]
        return element

    def has_control_element(self, control):
        return control in self._nested_control_elements

    def owns_control_element(self, control):
        return self._nested_control_elements.get(control, False)

    def owned_control_elements(self):
        return map(first, ifilter(second, self._nested_control_elements.iteritems()))

    def nested_control_elements(self):
        return self._nested_control_elements.iterkeys()

    def reset(self):
        for element in self.owned_control_elements():
            element.reset()

    def add_value_listener(self, *a, **k):
        if self.value_listener_count() == 0:
            self.request_listen_nested_control_elements()
        super(CompoundElement, self).add_value_listener(*a, **k)

    def remove_value_listener(self, *a, **k):
        super(CompoundElement, self).remove_value_listener(*a, **k)
        if self.value_listener_count() == 0:
            self.unrequest_listen_nested_control_elements()

    def request_listen_nested_control_elements(self):
        """
        By default, the compound control element will listen to its
        nested control elements IFF he himself has listeners.  This is
        important, because for nested InputControlElements, the
        existence of listeners determine wether they will send the
        MIDI messages to Live or to the script.
        
        You can force the compound to listen to its nested elements
        using this methods.  The compound will then listen to them IFF
        the number of requests is greater than the number of
        unrequests OR it has listeners.
        """
        if self._listen_nested_requests == 0:
            self._connect_nested_control_elements()
        self._listen_nested_requests += 1

    def unrequest_listen_nested_control_elements(self):
        """
        See request_listen_nested_control_elements()
        """
        if self._listen_nested_requests == 1:
            self._disconnect_nested_control_elements()
        self._listen_nested_requests -= 1

    def _connect_nested_control_elements(self):
        self._on_nested_control_element_value.replace_subjects(self._nested_control_elements.keys())

    def _disconnect_nested_control_elements(self):
        self._on_nested_control_element_value.replace_subjects([])

    def _on_nested_control_element_grabbed(self, control):
        if control in self._nested_control_elements:
            if not self._nested_control_elements[control]:
                self._nested_control_elements[control] = True
        self.on_nested_control_element_grabbed(control)

    def _on_nested_control_element_released(self, control):
        if control in self._nested_control_elements:
            if self._nested_control_elements[control]:
                self._nested_control_elements[control] = False
        self.on_nested_control_element_released(control)

    @subject_slot_group('value')
    def _on_nested_control_element_value(self, value, sender):
        if self.owns_control_element(sender):
            self.on_nested_control_element_value(value, sender)

    def set_control_element(self, control, grabbed):
        if grabbed:
            self._on_nested_control_element_grabbed(control)
        else:
            self._on_nested_control_element_released(control)
        owner = self._resource.owner
        if owner and not self._disable_notify_owner_on_button_ownership_change:
            self.notify_ownership_change(owner, True)

    def _on_grab_resource(self, client, *a, **k):
        was_resource_based = self._is_resource_based
        self._is_resource_based = True
        with self._disable_notify_owner_on_button_ownership_change():
            for element in self._nested_control_elements:
                if not was_resource_based:
                    element.notify_ownership_change(self, False)
                priority = self.get_control_element_priority(element)
                element.resource.grab(self, priority=priority, *a, **k)

            super(CompoundElement, self)._on_grab_resource(client, *a, **k)

    def _on_release_resource(self, client):
        raise self._is_resource_based or AssertionError
        with self._disable_notify_owner_on_button_ownership_change():
            super(CompoundElement, self)._on_release_resource(client)
            for element in self._nested_control_elements.keys():
                element.resource.release(self)