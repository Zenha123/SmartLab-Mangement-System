from unittest.mock import Mock, patch

from django.test import TestCase, override_settings

from apps.core.models import Batch, Semester
from apps.students.models import Student
from apps.students.services.etlab_sync import sync_students_from_etlab


@override_settings(ETLAB_SERVICE_TOKEN="test-token")
class EtlabStudentSyncTests(TestCase):
    @patch("apps.students.services.etlab_sync.requests.get")
    def test_students_are_split_into_two_default_batches_per_semester(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = [
            {"reg_number": "CS003", "name": "Student 3", "semester": "Sem 3"},
            {"reg_number": "CS001", "name": "Student 1", "semester": "Sem 3"},
            {"reg_number": "CS005", "name": "Student 5", "semester": "Sem 3"},
            {"reg_number": "CS002", "name": "Student 2", "semester": "Sem 3"},
            {"reg_number": "CS004", "name": "Student 4", "semester": "Sem 3"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = sync_students_from_etlab()

        semester = Semester.objects.get(number=3)
        batch_1 = Batch.objects.get(semester=semester, name="Batch 1")
        batch_2 = Batch.objects.get(semester=semester, name="Batch 2")

        self.assertEqual(result["synced"], 5)
        self.assertEqual(batch_1.total_students, 3)
        self.assertEqual(batch_2.total_students, 2)
        self.assertEqual(
            list(Student.objects.filter(batch=batch_1).order_by("student_id").values_list("student_id", flat=True)),
            ["CS001", "CS002", "CS003"],
        )
        self.assertEqual(
            list(Student.objects.filter(batch=batch_2).order_by("student_id").values_list("student_id", flat=True)),
            ["CS004", "CS005"],
        )

    @patch("apps.students.services.etlab_sync.requests.get")
    def test_resync_rebalances_existing_students_between_default_batches(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = [
            {"reg_number": "CS001", "name": "Student 1", "semester": "Sem 3"},
            {"reg_number": "CS002", "name": "Student 2", "semester": "Sem 3"},
            {"reg_number": "CS003", "name": "Student 3", "semester": "Sem 3"},
            {"reg_number": "CS004", "name": "Student 4", "semester": "Sem 3"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        sync_students_from_etlab()
        sync_students_from_etlab()

        semester = Semester.objects.get(number=3)
        batch_1 = Batch.objects.get(semester=semester, name="Batch 1")
        batch_2 = Batch.objects.get(semester=semester, name="Batch 2")

        self.assertEqual(batch_1.total_students, 2)
        self.assertEqual(batch_2.total_students, 2)
        self.assertEqual(Student.objects.filter(batch=batch_1).count(), 2)
        self.assertEqual(Student.objects.filter(batch=batch_2).count(), 2)
