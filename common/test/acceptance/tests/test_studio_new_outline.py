"""
Test new outline page.

selfie: paver test_bokchoy -t test_studio_new_outlie.py --fast
"""

from ..pages.studio.auto_auth import AutoAuthPage
from ..pages.studio.overview import CourseOutlinePage
from ..pages.studio.new_outline import NewCourseOutlinePage
from ..fixtures.course import CourseFixture, XBlockFixtureDesc

from .helpers import UniqueCourseTest
from ..pages.studio.component_editor import ComponentEditorView
from ..pages.studio.utils import add_discussion
from ..pages.lms.courseware import CoursewarePage

from unittest import skip
from bok_choy.promise import Promise, EmptyPromise


class NewCourseOutline(UniqueCourseTest):
    """
    Base class for tests that do operations on the container page.
    """
    __test__ = True

    def setUp(self):
        """
        Create a unique identifier for the course used in this test.
        """
        # Ensure that the superclass sets up
        super(NewCourseOutline, self).setUp()

        self.setup_fixtures()

        self.outline = NewCourseOutlinePage(
            self.browser,
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run']
        )

        self.auth_page = AutoAuthPage(
            self.browser,
            staff=True,
            username=self.user.get('username'),
            email=self.user.get('email'),
            password=self.user.get('password')
        )

        self.auth_page.visit()
        self.outline.visit()

    def setup_fixtures(self):
        course_fix = CourseFixture(
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run'],
            self.course_info['display_name']
        )
        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Section').add_children(
                XBlockFixtureDesc('sequential', 'Test Subsection').add_children(
                    XBlockFixtureDesc('vertical', 'Test Unit')
                )
            )
        ).install()
        self.course_fix = course_fix
        session = course_fix.session  # Need to initialize session in order to get user.
        self.user = course_fix.user


    def test_I_get_new_outline_page(self):
        """
        Go to the new outline page.
        """
        self.outline.visit()

    def test_I_can_edit_section(self):
        """
        I can edit section.
        """
        self.outline.edit_section()

        # chek that modal is section specific
        self.outline.modal_is_shown()

        self.outline.press_cancel_on_modal()

        self.outline.edit_section()
        self.outline.modal_is_shown()
        self.outline.press_save_on_modal()

    def test_I_can_edit_subsection(self):
        """
        I can edit subsection.
        """
        self.outline.edit_subsection()
        self.outline.modal_is_shown()

        # check that modal is subsection specific

        self.outline.press_cancel_on_modal()

        self.outline.edit_subsection()
        self.outline.modal_is_shown()
        self.outline.press_save_on_modal()


    def test_I_can_see_release_dates(self):
        self.assertTrue(self.outline.release_dates_present())

    def test_I_can_edit_release_date_subsection(self):
        self.outline.edit_subsection()
        self.outline.modal_is_shown()
        self.assertEqual(self.outline.release_date_in_modal(), u'01/01/70')
        self.outline.set_release_day(12)
        EmptyPromise(
            lambda: self.outline.release_date_in_modal() == u'1/12/1970',
            "Date is updated"
        ).fulfill()
        self.outline.press_save_on_modal()
        EmptyPromise(
            lambda: 'Released: Jan 12, 1970' in self.outline.subsection_release_date(),
            "Date is updated",
        ).fulfill()


    def test_I_can_edit_release_date_section(self):
        self.outline.edit_section()
        self.outline.modal_is_shown()
        self.assertEqual(self.outline.release_date_in_modal(), u'01/01/70')
        self.outline.set_release_day(14)
        EmptyPromise(
            lambda: self.outline.release_date_in_modal() == u'1/14/1970',
            "Date is updated"
        ).fulfill()
        self.outline.press_save_on_modal()
        EmptyPromise(
            lambda: 'Released: Jan 14, 1970' in self.outline.section_release_date(),
            "Date is updated",
        ).fulfill()

    def test_I_can_edit_due_date(self):
        self.outline.edit_subsection()
        self.outline.modal_is_shown()
        self.assertEqual(self.outline.due_date_in_modal(), u'')
        self.outline.set_due_day(21)
        EmptyPromise(
            lambda: self.outline.due_date_in_modal() == u'7/21/2014',
            "Date is updated"
        ).fulfill()
        self.outline.press_save_on_modal()
        EmptyPromise(
            lambda: 'Due: Jul 21, 2014' in self.outline.section_due_date(),
            "Date is updated",
        ).fulfill()


    # def test_I_can_grade_subsection(self):
    #     """
    #     I can grade subsection and see grading format after grading subsection.
    #     """
    #     self.outline.edit_subsection()
    #     self.outline.modal_is_shown()
    #     import ipdb; ipdb.set_trace()


