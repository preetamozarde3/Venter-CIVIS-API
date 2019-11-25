from datetime import datetime
from django.db import models
from django.core.validators import FileExtensionValidator
import os


class Organisation(models.Model):
    """
        An organisation that is associated with Venter application.
        Eg: xyz is an organisation associated with Venter
        # Create an organisation
        >>> organisation_1 = Organisation.objects.create(organisation_name="xyz")
    """
    organisation_name = models.CharField(
        max_length=200,
        primary_key=True,
    )

    def __str__(self):
        return self.organisation_name

    class Meta:
        """
        Declares a plural name for Organisation model
        """
        verbose_name_plural = 'Organisation'

class File(models.Model):
    """
        An output File created for a particular organisation.
        Eg: Organisation 'xyz' may have two or more output files per month.
        # Create a file instance
        >>> File.objects.create(organisation_name=xyz, ckpt_date = "Jan. 29, 2019, 7:59 p.m.")
    """        
    organisation_name = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
    )
    ckpt_date = models.DateTimeField(
        default=datetime.now,
    )
    output_file_json = models.FileField(
        blank=True, 
        max_length=255,
        validators=[FileExtensionValidator(allowed_extensions=['json'])],
    )
    wordcloud_data = models.FileField(
        blank=True,
        max_length=255,
        validators=[FileExtensionValidator(allowed_extensions=['json'])],
    )

    @property
    def output_filename(self):
        """
        Returns the name of the ml output file created.
        Usage: views.py
        """
        return os.path.basename(self.output_file_json.name)  # pylint: disable = E1101

    @property
    def wordcloud_filename(self):
        """
        Returns the name of the wordcloud file generated.
        Usage: views.py
        """
        return os.path.basename(self.wordcloud_data.name)  # pylint: disable = E1101        

    def delete(self):
        """
        Deletes json output/wordcloud files from file storage
        Usage: views.py
        """
        if self.output_file_json:
            default_storage.delete(self.output_file_json)
        if self.wordcloud_data:
            default_storage.delete(self.wordcloud_data)
        super().delete()

    class Meta:
        """
        Declares a plural name for File model
        """
        verbose_name_plural = 'File'        

class Draft(models.Model):
    """
        A Draft is added for a particular organisation
        # Create a draft instance
        >>> Draft.objects.create(organisation_name=xyz, creation_date = "Jan. 29, 2019, 7:59 p.m.", draft_name='abc')
    """        
    organisation_name = models.ForeignKey(
        Organisation,
        on_delete = models.CASCADE,
    )
    draft_name = models.CharField(
        max_length = 255,
        unique=True,
    )
    creation_date = models.DateTimeField(
        default=datetime.now,
    )
    ml_output = models.ForeignKey(
        File,
        on_delete = models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.draft_name

    class Meta:
        """
        Declares a plural name for Draft model
        """
        verbose_name_plural = 'Draft'

class Category(models.Model):
    """
        A Category list associated with each organisation.
        Eg: Organisation xyz may contain categories in the csv file such as- hawkers, garbage etc
        # Create a category instance
        >>> Category.objects.create(draft_name="xyz", category="hawkers")
    """
    draft_name = models.ForeignKey(
        Draft,
        on_delete=models.CASCADE,
        blank=True, 
        null=True,
    )
    category = models.CharField(
        max_length=255
    )

    class Meta:
        """
        Declares a plural name for Category model
        """
        verbose_name_plural = 'Category'


class SentenceCategory(models.Model):
    """
        A Category list associated with each organisation.
        Eg: Organisation xyz may contain categories in the csv file such as- hawkers, garbage etc
        # Create a category instance
        >>> Category.objects.create(draft_name="xyz", category="hawkers")
    """
    draft_name = models.ForeignKey(
        Draft,
        on_delete=models.CASCADE,
        blank=True, 
        null=True,
    )
    category = models.CharField(
        max_length=255
    )

    class Meta:
        """
        Declares a plural name for Category model
        """
        verbose_name_plural = 'Sentence Category'

class UserResponse(models.Model):
    """
        A User entered response is added for a particular draft
        Eg: User response 'potholes on road' will have one draft name associated with it e.g 'Bad roads'
        # Create a user response instance
        >>> UserResponse.objects.create(draft_name=draft_name,  user_response='potholes on road', creation_date = "Jan. 29, 2019, 7:59 p.m.")
    """        
    draft_name = models.ForeignKey(
        Draft,
        on_delete = models.CASCADE,
    )
    user_response = models.CharField(
        max_length=5000
    )
    creation_date = models.DateTimeField(
        default=datetime.now,
    )

    def __str__(self):
        return self.user_response
    
    class Meta:
        """
        Declares a plural name for UserResponse model
        """
        verbose_name_plural = 'User Response'
