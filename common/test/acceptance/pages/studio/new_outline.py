"""
New `Course Outline` page in Studio.
"""
from bok_choy.page_object import PageObject
from bok_choy.promise import EmptyPromise

from .course_page import CoursePage
from .container import ContainerPage
from .utils import set_input_value_and_save


class NewCourseOutlinePage(CoursePage):
    """
    New `Course Outline` page in Studio.
    """
    url_path = "course"

    def is_browser_on_page(self):
        return self.q(css='body.view-outline').present

    def edit_section(self):
        self.q(css=".icon-gear").first.click()

    def edit_subsection(self):
        self.q(css=".icon-gear").nth(1).click()

    def modal_is_shown(self):
        self.q(css=".edit-xblock-modal").present

    def modal_is_section_specific(self):
        self.q(css="#start_date").present
        self.q(css="#start_time").present
        not self.q(css="#due_date").present
        not self.q(css="#due_time").present
        not self.q(css="#grading_type").present

    def modal_is_subsection_specific(self):
        self.q(css="#start_date").present
        self.q(css="#start_time").present
        self.q(css="#due_date").present
        self.q(css="#due_time").present
        self.q(css="#grading_type").present

    def press_cancel_on_modal(self):
        self.q(css=".action-cancel").present
        self.q(css=".action-cancel").first.click()

    def press_save_on_modal(self):
        self.q(css=".action-save").present
        self.q(css=".action-save").first.click()
        self.wait_for_ajax()

    def release_dates_present(self):
        dates = self.q(css="div.meta-info").text
        return all([text == u'Released: Jan 01, 1970 at 00:00 UTC' for text in dates])

    def section_release_date(self):
        return self.q(css="div.meta-info").first.text[0]

    def subsection_release_date(self):
        return self.q(css="div.meta-info").nth(1).text[0]

    def subsection_info(self):
        return self.q(css="div.meta-info").nth(1).text[0]

    def due_date_present(self):
        due_date = self.q(css="div.meta-info").nth(1).text
        return all([text == u'Released: Jan 01, 1970 at 00:00 UTC' for text in dates])

    def release_date_in_modal(self):
        return self.q(css="#start_date").first.attrs('value')[0]

    def due_date_in_modal(self):
        return self.q(css="#due_date").first.attrs('value')[0]

    def set_release_day(self, day_number):
        self.q(css="#start_date").first.click()
        self.q(css="a.ui-state-default").nth(day_number-1).click()

    def set_due_day(self, day_number):
        self.q(css="#due_date").first.click()
        self.q(css="a.ui-state-default").nth(day_number-1).click()

    def select_grading_format(self, grading_format):
        """
        Select the grading format with `value` in the drop-down list.
        """
        self.q(css='select[id="grading_type"] option[value="{}"]'.format(grading_format)).first.click()

    def is_grading_format_selected(self, grading_format):
        return self.q(css='select[id="grading_type"] option[value="{}"]'.format(grading_format)).selected

