"""
Test new outline page.

selfie: paver test_bokchoy -t test_studio_new_outlie.py --fast
"""

from ..pages.studio.auto_auth import AutoAuthPage
from ..pages.studio.overview import CourseOutlinePage
from ..pages.studio.new_outline import NewCourseOutlinePage
from ..fixtures.course import CourseFixture, XBlockFixtureDesc

from .helpers import UniqueCourseTest, load_data_str
from ..pages.studio.component_editor import ComponentEditorView
from ..pages.studio.utils import add_discussion
from ..pages.lms.courseware import CoursewarePage
from ..pages.lms.course_page import CoursePage
from ..pages.lms.progress import ProgressPage
from ..pages.lms.course_info import CourseInfoPage

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
                    XBlockFixtureDesc('vertical', 'Test Unit').add_children(
                        XBlockFixtureDesc('problem', 'Test Problem 1', data=load_data_str('multiple_choice.xml')),
                    )
                )
            )
        ).install()
        self.course_fix = course_fix
        session = course_fix.session  # Need to initialize session in order to get user.
        self.user = course_fix.user
        self.progress_page = ProgressPage(self.browser, self.course_id)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)


    def test_I_get_new_outline_page(self):
        """
        Verify that I can go to the new outline page.
        """
        self.outline.visit()

    def test_I_can_edit_section(self):
        """
        Verify that I can see section specific edit modal and press save/cancel buttons.
        """
        self.outline.edit_section()
        self.outline.modal_is_shown()
        self.outline.modal_is_section_specific()
        self.outline.press_cancel_on_modal()

        self.outline.edit_section()
        self.outline.modal_is_shown()
        self.outline.press_save_on_modal()

    def test_I_can_edit_subsection(self):
        """
        Verify that I can see subsection specific edit modal and press save/cancel buttons.
        """
        self.outline.edit_subsection()
        self.outline.modal_is_shown()
        self.outline.modal_is_subsection_specific()
        self.outline.press_cancel_on_modal()

        self.outline.edit_subsection()
        self.outline.modal_is_shown()
        self.outline.press_save_on_modal()

    def test_I_can_see_release_dates(self):
        """
        Verify that I can see release dates in course outline.
        """
        self.assertTrue(self.outline.release_dates_present())

    def test_I_can_edit_release_date_subsection(self):
        """
        Verify that I can edit release date of subsection.
        """
        self.outline.edit_subsection()
        self.outline.modal_is_shown()
        self.assertEqual(self.outline.release_date_in_modal(), u'1/1/1970')
        self.outline.set_release_day(12)
        EmptyPromise(
            lambda: self.outline.release_date_in_modal() == u'1/12/1970',
            "Release date of subsection is updated in modal."
        ).fulfill()
        self.outline.press_save_on_modal()
        EmptyPromise(
            lambda: 'Released: Jan 12, 1970' in self.outline.subsection_info(),
            "Release date of subsection is updated in course outline.",
        ).fulfill()

    def test_I_can_edit_release_date_section(self):
        """
        Verify that I can edit release date of section.
        """
        self.outline.edit_section()
        self.outline.modal_is_shown()
        self.assertEqual(self.outline.release_date_in_modal(), u'1/1/1970')
        self.outline.set_release_day(14)
        EmptyPromise(
            lambda: self.outline.release_date_in_modal() == u'1/14/1970',
            "Release date of section is updated in modal."
        ).fulfill()
        self.outline.press_save_on_modal()
        EmptyPromise(
            lambda: 'Released: Jan 14, 1970' in self.outline.section_release_date(),
            "Release date of section is updated in course outline.",
        ).fulfill()

    def test_I_can_edit_due_date(self):
        """
        Verify that I can edit due date of subsection.
        """
        self.outline.edit_subsection()
        self.outline.modal_is_shown()
        self.assertEqual(self.outline.due_date_in_modal(), u'')
        self.outline.set_due_day(21)
        EmptyPromise(
            lambda: self.outline.due_date_in_modal() == u'7/21/2014',
            "Due date of subsection is updated in modal."
        ).fulfill()
        self.outline.press_save_on_modal()
        EmptyPromise(
            lambda: 'Due date: Jul 21, 2014' in self.outline.subsection_info(),
            "Due date of subsection is updated in course outline.",
        ).fulfill()


    def test_I_can_grade_subsection(self):
        """
        Verify that I can grade subsection and see grading format in course outline.
        """
        self.outline.edit_subsection()
        self.outline.modal_is_shown()
        self.assertTrue(self.outline.is_grading_format_selected('notgraded'))
        self.outline.select_grading_format('Lab')
        self.assertTrue(self.outline.is_grading_format_selected('Lab'))
        self.outline.set_due_day(21)
        EmptyPromise(
            lambda: self.outline.due_date_in_modal() == u'7/21/2014',
            "Due date of subsection is updated in modal."
        ).fulfill()
        self.outline.press_save_on_modal()
        EmptyPromise(
            lambda: 'Policy: Lab' in self.outline.subsection_info(),
            "Grading format of subsection is updated in course outline.",
        ).fulfill()

    def test_I_can_grade_subsection_wo_due_date(self):
        """
        Verify that I can grade subsection w/o setting due date 
        and see grading format in course outline.
        """
        self.outline.edit_subsection()
        self.outline.modal_is_shown()
        self.assertTrue(self.outline.is_grading_format_selected('notgraded'))
        self.outline.select_grading_format('Lab')
        self.assertTrue(self.outline.is_grading_format_selected('Lab'))
        self.outline.press_save_on_modal()
        EmptyPromise(
            lambda: 'Policy: Lab' in self.outline.subsection_info(),
            "Grading format of subsection is updated in course outline.",
        ).fulfill()


    def test_I_can_grade_subsection_and_subsection_is_graded(self):
        """
        Verify that I can grade subsection and it is graded in LMS.
        """
        self.progress_page.visit()
        self.assertTrue(u'Practice Scores:', self.progress_page.q(css="div.scores h3").text[0])
        self.outline.visit()
        self.test_I_can_grade_subsection()
        self.progress_page.visit()
        self.assertTrue(u'Problem Scores:', self.progress_page.q(css="div.scores h3").text[0])
