"""
Course Outline page in Studio.
"""
import datetime

from bok_choy.page_object import PageObject
from bok_choy.promise import EmptyPromise

from selenium.webdriver.support.ui import Select

from .course_page import CoursePage
from .container import ContainerPage
from .utils import set_input_value_and_save


class CourseOutlineItem(object):
    """
    A mixin class for any :class:`PageObject` shown in a course outline.
    """
    BODY_SELECTOR = None
    EDIT_BUTTON_SELECTOR = '.xblock-title .xblock-field-value-edit'
    NAME_SELECTOR = '.xblock-title .xblock-field-value'
    NAME_INPUT_SELECTOR = '.xblock-title .xblock-field-input'
    CONFIGURATION_BUTTON_SELECTOR = '.item-actions .configure-button'

    def __repr__(self):
        return "{}(<browser>, {!r})".format(self.__class__.__name__, self.locator)

    def _bounded_selector(self, selector):
        """
        Returns `selector`, but limited to this particular `CourseOutlineItem` context
        """
        return '{}[data-locator="{}"] {}'.format(
            self.BODY_SELECTOR,
            self.locator,
            selector
        )

    @property
    def name(self):
        """
        Returns the display name of this object.
        """
        name_element = self.q(css=self._bounded_selector(self.NAME_SELECTOR)).first
        if name_element:
            return name_element.text[0]
        else:
            return None

    def change_name(self, new_name):
        """
        Changes the container's name.
        """
        self.q(css=self._bounded_selector(self.EDIT_BUTTON_SELECTOR)).first.click()
        set_input_value_and_save(self, self._bounded_selector(self.NAME_INPUT_SELECTOR), new_name)
        self.wait_for_ajax()

    def edit(self):
        self.q(css=self._bounded_selector(self.CONFIGURATION_BUTTON_SELECTOR)).first.click()
        modal = ItemOutlineModal(self)
        EmptyPromise(lambda: modal.is_shown(), 'Modal is shown.')
        return modal

    @property
    def release_date(self):
        return self.q(css=self._bounded_selector(".release-date")).first.text[0]

    @property
    def due_date(self):
        return self.q(css=self._bounded_selector(".due-date")).first.text[0]

    @property
    def policy(self):
        return self.q(css=self._bounded_selector(".policy")).first.text[0]


class CourseOutlineContainer(CourseOutlineItem):
    """
    A mixin to a CourseOutline page object that adds the ability to load
    a child page object by title or by index.

    CHILD_CLASS must be a :class:`CourseOutlineChild` subclass.
    """
    CHILD_CLASS = None

    def child(self, title, child_class=None):
        """

        :type self: object
        """
        if not child_class:
            child_class = self.CHILD_CLASS

        return child_class(
            self.browser,
            self.q(css=child_class.BODY_SELECTOR).filter(
                lambda el: title in [inner.text for inner in
                                     el.find_elements_by_css_selector(child_class.NAME_SELECTOR)]
            ).attrs('data-locator')[0]
        )

    def child_at(self, index, child_class=None):
        """
        Returns the child at the specified index.
        :type self: object
        """
        if not child_class:
            child_class = self.CHILD_CLASS

        return child_class(
            self.browser,
            self.q(css=child_class.BODY_SELECTOR).attrs('data-locator')[index]
        )


class CourseOutlineChild(PageObject, CourseOutlineItem):
    """
    A page object that will be used as a child of :class:`CourseOutlineContainer`.
    """
    def __init__(self, browser, locator):
        super(CourseOutlineChild, self).__init__(browser)
        self.locator = locator

    def is_browser_on_page(self):
        return self.q(css='{}[data-locator="{}"]'.format(self.BODY_SELECTOR, self.locator)).present


class CourseOutlineUnit(CourseOutlineChild):
    """
    PageObject that wraps a unit link on the Studio Course Overview page.
    """
    url = None
    BODY_SELECTOR = '.outline-item-unit'
    NAME_SELECTOR = '.xblock-title a'

    def go_to(self):
        """
        Open the container page linked to by this unit link, and return
        an initialized :class:`.ContainerPage` for that unit.
        """
        return ContainerPage(self.browser, self.locator).visit()


class CourseOutlineSubsection(CourseOutlineChild, CourseOutlineContainer):
    """
    :class`.PageObject` that wraps a subsection block on the Studio Course Overview page.
    """
    url = None

    BODY_SELECTOR = '.outline-item-subsection'
    CHILD_CLASS = CourseOutlineUnit

    def unit(self, title):
        """
        Return the :class:`.CourseOutlineUnit with the title `title`.
        """
        return self.child(title)

    def toggle_expand(self):
        """
        Toggle the expansion of this subsection.
        """
        self.browser.execute_script("jQuery.fx.off = true;")

        def subsection_expanded():
            add_button = self.q(css=self._bounded_selector('.add-button')).first.results
            return add_button and add_button[0].is_displayed()

        currently_expanded = subsection_expanded()

        self.q(css=self._bounded_selector('.ui-toggle-expansion')).first.click()

        EmptyPromise(
            lambda: subsection_expanded() != currently_expanded,
            "Check that the subsection {} has been toggled".format(self.locator)
        ).fulfill()

        return self


class CourseOutlineSection(CourseOutlineChild, CourseOutlineContainer):
    """
    :class`.PageObject` that wraps a section block on the Studio Course Overview page.
    """
    url = None
    BODY_SELECTOR = '.outline-item-section'
    CHILD_CLASS = CourseOutlineSubsection

    def subsection(self, title):
        """
        Return the :class:`.CourseOutlineSubsection` with the title `title`.
        """
        return self.child(title)


class CourseOutlinePage(CoursePage, CourseOutlineContainer):
    """
    Course Outline page in Studio.
    """
    url_path = "course"
    CHILD_CLASS = CourseOutlineSection

    def is_browser_on_page(self):
        return self.q(css='body.view-outline').present

    def section(self, title):
        """
        Return the :class:`.CourseOutlineSection` with the title `title`.
        """
        return self.child(title)

    def section_at(self, index):
        """
        Returns the :class:`.CourseOutlineSection` at the specified index.
        """
        return self.child_at(index)


class ItemOutlineModal(object):
    MODAL_SELECTOR = ".edit-outline-item-modal"

    def __init__(self, page):
        self.page = page

    def _bounded_selector(self, selector):
        """
        Returns `selector`, but limited to this particular `ItemOutlineModal` context.
        """
        return " ".join([self.MODAL_SELECTOR, selector])

    def is_shown(self):
        return self.page.q(css=self.MODAL_SELECTOR).present

    def find_css(self, selector):
        return self.page.q(css=self._bounded_selector(selector))

    def click(self, selector, index=0):
        self.find_css(selector).nth(index).click()

    def save(self):
        self.click(".action-save")
        self.page.wait_for_ajax()

    def cancel(self):
        self.click(".action-cancel")

    def has_release_date(self):
        return self.find_css("#start_date").present

    def has_due_date(self):
        return self.find_css("#due_date").present

    def has_grading_type(self):
        return self.find_css("#grading_type").present

    @property
    def release_date(self):
        return self.find_css("#start_date").first.attrs('value')[0]

    @release_date.setter
    def release_date(self, day_number):
        self.click("#start_date")
        self.page.q(css="a.ui-state-default").nth(day_number - 1).click()
        EmptyPromise(
            lambda: self.release_date == u'1/{}/1970'.format(day_number),
            "Release date is updated in modal."
        ).fulfill()

    @property
    def due_date(self):
        return self.find_css("#due_date").first.attrs('value')[0]

    @due_date.setter
    def due_date(self, day_number):
        now = datetime.datetime.now()
        self.click("#due_date")
        self.page.q(css="a.ui-state-default").nth(day_number - 1).click()
        EmptyPromise(
            lambda: self.due_date == '{}/{}/{}'.format(now.month, day_number, now.year),
            "Due date is updated in modal."
        ).fulfill()

    @property
    def policy(self):
        """
        Select the grading format with `value` in the drop-down list.
        """
        element = self.find_css('#grading_type')[0]
        return self.get_selected_option_text(element)

    @policy.setter
    def policy(self, grading_label):
        """
        Select the grading format with `value` in the drop-down list.
        """
        element = self.find_css('#grading_type')[0]
        select = Select(element)
        select.select_by_visible_text(grading_label)

        EmptyPromise(
            lambda: self.policy == grading_label,
            "Grading label is updated.",
        ).fulfill()

    def is_grading_label_selected(self, grading_label):
        element = self.find_css('#grading_type')[0]
        return self.get_selected_option_text(element) == grading_label

    def get_selected_option_text(self, element):
        """
        Returns the text of the first selected option for the select with given label (display name).
        """
        if element:
            select = Select(element)
            return select.first_selected_option.text
        else:
            return None
