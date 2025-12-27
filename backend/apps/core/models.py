from django.db import models


class Semester(models.Model):
    """Academic semester (e.g., Sem 1, Sem 2, etc.)"""
    name = models.CharField(max_length=50)  # e.g., "Sem 1"
    number = models.IntegerField(unique=True)  # 1-8
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'semesters'
        ordering = ['number']
    
    def __str__(self):
        return self.name


class Batch(models.Model):
    """Batch within a semester (e.g., Batch 1, Batch 2)"""
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='batches')
    name = models.CharField(max_length=50)  # e.g., "Batch 1"
    year = models.IntegerField()  # Academic year
    total_students = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'batches'
        ordering = ['semester__number', 'name']
        unique_together = ['semester', 'name']
    
    def __str__(self):
        return f"{self.semester.name} - {self.name}"


class PCMapping(models.Model):
    """Maps students to specific PC IDs in the lab"""
    pc_id = models.CharField(max_length=20, unique=True, db_index=True)  # e.g., "PC-01"
    student = models.OneToOneField('students.Student', on_delete=models.SET_NULL, null=True, blank=True, related_name='pc_mapping')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='pc_mappings')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pc_mappings'
        ordering = ['pc_id']
    
    def __str__(self):
        student_name = self.student.name if self.student else "Unassigned"
        return f"{self.pc_id} - {student_name}"
