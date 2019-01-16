{
    'name': 'Student Enquiry Website',
    'version': '1.0',
    'category': 'Edsys Education',
    "sequence": 3,
    'summary': 'Manage Students, Faculties and Education Institute',
    'complexity': "easy",
    'description': """
            This module provide overall education management system over OpenERP
            Features includes managing
                * Student
                * Faculty
                * Admission
                * Course
                * Batch
                * Books
                * Library
                * Lectures
                * Exams
                * Marksheet
                * Result
                * Transportation
                * Hostel

    """,
    'author': 'Edsys',
    'website': 'https://www.edsys.in/',
    'depends': ['base','website','edsys_edu','document'],
    'data': [
              'view/website_student_enquiry.xml',
              'data/config_data.xml',
              'view/enquiry_templates.xml',
              'view/email_templet.xml',
              'view/student_information_templet.xml',
              'view/student_verification_templet.xml',
              'view/student_other_info_templet.xml',
             ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
