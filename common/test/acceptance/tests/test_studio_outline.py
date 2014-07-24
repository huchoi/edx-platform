"""
Tests for course outline page.
"""
from ..pages.studio.auto_auth import AutoAuthPage
from ..pages.studio.overview import CourseOutlinePage
from ..fixtures.course import CourseFixture, XBlockFixtureDesc

from .helpers import UniqueCourseTest, load_data_str
from ..pages.lms.progress import ProgressPage


SECTION_NAME = 'Test Section'
SUBSECTION_NAME = 'Test Subsection'
UNIT_NAME = 'Test Unit'


class CourseOutlineTest(UniqueCourseTest):
    """
    Base class for tests that do operations on the course outline page.
    """
    __test__ = True

    def setUp(self):
        """
        Create a unique identifier for the course used in this test.
        """
        # Ensure that the superclass sets up
        super(CourseOutlineTest, self).setUp()

        self.setup_fixtures()

        self.outline = CourseOutlinePage(
            self.browser,
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run'],
        )

        self.auth_page = AutoAuthPage(
            self.browser,
            staff=True,
            username=self.user.get('username'),
            email=self.user.get('email'),
            password=self.user.get('password'),
        )

        self.auth_page.visit()
        self.outline.visit()

    def setup_fixtures(self):
        course_fix = CourseFixture(
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run'],
            self.course_info['display_name'],
        )
        course_fix.add_children(
            XBlockFixtureDesc('chapter', SECTION_NAME).add_children(
                XBlockFixtureDesc('sequential', SUBSECTION_NAME).add_children(
                    XBlockFixtureDesc('vertical', UNIT_NAME).add_children(
                        XBlockFixtureDesc('problem', 'Test Problem 1', data=load_data_str('multiple_choice.xml')),
                    )
                )
            )
        ).install()
        self.course_fix = course_fix
        self.user = course_fix.user
        self.progress_page = ProgressPage(self.browser, self.course_id)

    def test_can_edit_subsection(self):
        """
        Verify that I can edit release date of subsection.
        """
        subsection = self.outline.section(SECTION_NAME).subsection(SUBSECTION_NAME)

        # Verify that Release date visible by default
        self.assertTrue(subsection.release_date)
        # Verify that Due date and Policy hidden by default
        self.assertFalse(subsection.due_date)
        self.assertFalse(subsection.policy)

        modal = subsection.edit()

        # Verify fields
        self.assertTrue(modal.has_release_date())
        self.assertTrue(modal.has_due_date())
        self.assertTrue(modal.has_policy())

        # Verify initial values
        self.assertEqual(modal.release_date, u'1/1/1970')
        self.assertEqual(modal.due_date, u'')
        self.assertEqual(modal.policy, u'Not Graded')

        # Set new values
        modal.release_date = 12
        modal.due_date = 21
        modal.policy = 'Lab'

        modal.save()
        self.assertIn(u'Released: Jan 12, 1970', subsection.release_date)
        self.assertIn(u'Due date: Jul 21, 2014', subsection.due_date)
        self.assertIn(u'Policy: Lab', subsection.policy)

    def test_can_edit_section(self):
        """
        Verify that I can edit release date of section.
        """
        section = self.outline.section(SECTION_NAME)
        modal = section.edit()

        # Verify that Release date visible by default
        self.assertTrue(section.release_date)
        # Verify that Due date and Policy are not present
        self.assertFalse(section.due_date)
        self.assertFalse(section.policy)

        # Verify fields
        self.assertTrue(modal.has_release_date())
        self.assertFalse(modal.has_due_date())
        self.assertFalse(modal.has_policy())

        # Verify initial value
        self.assertEqual(modal.release_date, u'1/1/1970')

        # Set new value
        modal.release_date = 14

        modal.save()
        self.assertIn(u'Released: Jan 14, 1970', section.release_date)
        # Verify that Due date and Policy are not present
        self.assertFalse(section.due_date)
        self.assertFalse(section.policy)

    def test_subsection_is_graded_in_lms(self):
        """
        Verify that I can grade subsection and it is graded in LMS.
        """
        self.progress_page.visit()
        self.assertEqual(u'Practice', self.progress_page.grading_formats[0])
        self.outline.visit()

        subsection = self.outline.section(SECTION_NAME).subsection(SUBSECTION_NAME)
        modal = subsection.edit()
        # Set new values
        modal.policy = 'Lab'
        modal.save()

        self.progress_page.visit()

        self.assertEqual(u'Problem', self.progress_page.grading_formats[0])
