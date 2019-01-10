from openerp import models, fields, api, _

class PaperLessStudent(models.Model):

    _inherit = 'res.partner'

    default_page = fields.Boolean('Default Page')
    is_fill_page1 = fields.Boolean('Page1')
    is_fill_page2 = fields.Boolean('Page2')
    is_fill_page3 = fields.Boolean('Page3')
    is_fill_page4 = fields.Boolean('Page4')
    is_fill_page5 = fields.Boolean('Page5')
    is_fill_page6 = fields.Boolean('Page6')
    postal_address = fields.Text('Postal Address')
    student_is_living_with = fields.Char('Student is living with')
    lang_spoken_at_home = fields.Many2many('res.lang',
                                               string='Language(s) spoken at home')
    english_is_spoken_at_home = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                 string="English is spoken at home (Yes / No)")
    english_written = fields.Selection([('none', 'None'), ('some', 'Some'),
                                        ('satisfactory', 'Satisfactory'),
                                        ('proficient', 'Proficient')], string="Written")
    english_spoken = fields.Selection([('none', 'None'), ('some', 'Some'),
                                       ('satisfactory', 'Satisfactory'),
                                       ('proficient', 'Proficient')], string="Spoken")
    english_reading = fields.Selection([('none', 'None'), ('some', 'Some'),
                                        ('satisfactory', 'Satisfactory'),
                                        ('proficient', 'Proficient')], string="Reading")
    father_nationality = fields.Many2one('res.country', string="Father Nationality")
    father_passport = fields.Char('Father Passport')
    father_emirates_id = fields.Char('Father Passport')
    # father_designation = fields.Char('Father Designation')
    mother_nationality = fields.Many2one('res.country', string="Mother Nationality")
    mother_passport = fields.Char('Mother Passport')
    mother_emirates_id = fields.Char('Mother Passport')
    # mother_designation = fields.Char('Mother Designation')
    special_contribution_list = [('substitute_teaching', 'Substitute Teaching'),
                                 ('classroom_volunteer', 'Classroom Volunteer'),
                                 ('field_trip_volunteer', 'Field Trip Volunteer'),
                                 ('library_assistance', 'Library Assistance'),
                                 ('drama', 'Drama'),
                                 ('art', 'Art'),
                                 ('specialised_teaching_of_music', 'Specialised Teaching of Music'),
                                 ('talking_to_children_describing_some_aspect_of_your','Talking to Children Describing some Aspect of your Work or Hobbies'),
                                 ('any_other','Any other')]
    spe_contribution = fields.Selection(special_contribution_list,
                                            string='Special Contribution')
    special_contribution_any_other = fields.Char('Any Other')
    medium_of_instruction = fields.Char('Medium of Instruction')
    received_double_promotion = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                 string="Has your child ever received a double promotion")
    identified_gifted_or_talented = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                     string="Has your child ever been identified as gifted or talented ?")
    has_child_detained = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                          string="Has your child ever been detained ?")
    has_child_detained_grade = fields.Many2one('course','Grade')
    child_received_academic_distinction = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                           string="Has your child received any academic distinction ?")
    child_received_academic_distinction_details = fields.Char(string='If yes, please indicate details')
    has_suspended_expelled_by_school = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                        string="Has your child ever been suspended/ expelled by any school in the past ?")
    has_suspended_expelled_by_school_details = fields.Char(string='If yes, please indicate details')
    child_associated_with_awareness = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                       string="Has your child been associated with any social awareness programme?")
    child_associated_with_awareness_details = fields.Char(string='If yes, please indicate details')
    member_of_environment_protection = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                        string="Has your child been a member of environment protection group ?")
    member_of_environment_protection_details = fields.Char(string='If yes, please indicate details')
    leadership_positions_in_school = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                      string="Has your child held any leadership positions in School? (Prefectorial Board/ Student Council)")
    leadership_positions_in_school_details = fields.Char(string='If yes, please indicate details')
    special_education_programme = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                   string="Has your child ever been in a speech therapy, remedial reading support, special education programme?")
    special_education_programme_details = fields.Char(string='If yes, please indicate details')
    special_learning_disability = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                   string="Has your child ever been identified as having a special learning disability?")
    special_learning_disability_details = fields.Selection(
        [('reading', 'Reading'), ('language', 'Language'), ('mathematics', 'Mathematics')],
        string="If yes, please indicate learning disability area")
    has_other_than_english_languages = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                        string="Has your child ever studied any languages other than English ?")
    other_than_english_languages = fields.Many2one('res.lang', 'If yes, please mention the other languages')
    hobbies_interests = fields.Text("Please list your child's hobbies / interests")
    has_play_any_musical_instrument = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                       string="Does your child play any musical instrument ?")
    musical_instrument_details = fields.Char(string='If yes, please specify')
    has_formal_training_in_music = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                    string="Has your child had any formal training in music ?")
    training_in_music_details = fields.Char(string='If yes, please give details')
    sport_child_play = fields.Char(string='Which sport does your child play ?')
    has_training_or_interest_art = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                    string="Has your child had any training / shown interest in fine arts ?")
    has_training_or_interest_art_details = fields.Char(string='If yes, please give details')
    inter_school_competitions = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                 string="Has your child participated in inter/ intra school competitions?")
    inter_school_competitions_details = fields.Char(string='If yes, please give details')
    special_activity_interested = fields.Char(string='Any other special activity your child is interested in?')

    adjusts_new_situations_with_ease = fields.Boolean('Adjusts to new situations with ease')
    has_small_group_of_friends = fields.Boolean('Has a small group of friends')
    has_never_adjust_new_situation = fields.Boolean('Has never had to adjust to a new situation')
    has_many_friends = fields.Boolean('Has many friends')
    likes_be_active_in_school = fields.Boolean('Likes to be active in school')
    expressions_describe_your_child = fields.Selection([('very_active', 'Very Active'), ('very_quiet', 'Very Quiet'),
                                                        ('average', 'Average'), ('above_average', 'Above Average'),
                                                        ('shy', 'Shy'), ('sociable', 'Sociable'),
                                                        ('aggressive', 'Aggressive'), ('other', 'Other')],
                                                       string='Please Select the expression that describe your child.')
    social_emotional_behavioural_difficulties = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                                 string="Has your child ever experienced social, emotional or behavioural difficulties?")
    social_emotional_behavioural_difficulties_details = fields.Char('If yes, please mention the details')
    useful_information_for_educating = fields.Char(string='Is there any other information you feel would be useful for those educating your child?')
    person_to_call = fields.Char('Person to call')
    emergency_relationship = fields.Char(string='Relationship')
    # emergency_tel_no = fields.Char(string='Tel. Nos. to call')
    has_use_bus_facility = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                            string="Would your child be using bus facility?")
    normal_delivery = fields.Char('Normal delivery')
    caesarean = fields.Char('Caesarean')
    premature = fields.Char('Premature')
    developmental_milestones = fields.Char('Developmental Milestones')
    age_your_child_talk = fields.Char('At what age did your child talk? (14 months +)')
    hand_preference = fields.Selection([('left', 'Left'), ('right', 'Right'),('both', 'Both')],
                                       string="Hand Preference")
    can_button_his_shirt = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                            string='Can the child button his shirt ?')
    can_zip_his_pant = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                        string='Can the child zip his pant ?')
    can_child_indicate_his_toilet_needs = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                           string = 'Can the child indicate his toilet needs?')
    child_indicate_his_toilet_needs_details = fields.Char('If yes, how?')
    child_know_his_phone_number = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                   string='Does your child know his phone number?')
    toys_likes_to_play_with = fields.Char('What are the toys he / she likes to play with?')
    special_interest = fields.Char('Any special interest that your child has?')
    child_like_to_play_with = fields.Char(string='Does your child like to play: alone / with friends / with family members')
    child_like_to_look_at_picture = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                     string='Does your child like to look at picture books?')
    child_like_to_watch_tv_programmes = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                         string='Does your child like to watch TV programmes?')
    channels_like_to_watch = fields.Char('What channels does he / she watch?')
    child_have_any_health_problem = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                     string='Does your child have any health problem?')
    health_problem_details = fields.Char('If yes, what?')
    health_card_no = fields.Char('Health Card No')

    diphtheria = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Diphtheria')
    accident = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Accident')
    dysentery = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Dysentery')
    allergies = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Allergies')
    infective_hepatitis = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Infective Hepatitis')
    bronchial_asthma =  fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Bronchial Asthma')
    measles = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Measles')
    congenital_heart_disease = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Congenital Heart Disease')
    mumps = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Mumps')
    diabetes_mellitus = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Diabetes mellitus')
    poliomyelitis = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Poliomyelitis')
    epilepsy = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Epilepsy')
    rubella = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Rubella')
    G6PD = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='G6PD (Glucose 6 phosphate dehydrogenase deficiency)')
    scarlet_fever = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Scarlet fever')
    rheumatic_fever = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Rheumatic fever')
    tuberculosis = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Tuberculosis')
    surgical_operation = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Surgical Operation')
    whooping_cough = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Whooping cough')
    thalassemia = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Thalassemia')
    chicken_pox = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Chicken Pox')
    physically_challenged = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Physically Challenged')
    infectious_disease_other = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Others')
    hearing_speech_defect = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Hearing/speech defect')
    vision_problems = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Vision Problems')
    history_of_blood_transfusion = fields.Selection([('yes', 'YES'), ('no', 'NO'),('frequency','Frequency')],
                                                    string='History of blood transfusion')
    hospitalization = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Hospitalization')
    hospitalization_reason = fields.Char(string='Reason')
    HTN = fields.Boolean('HTN')
    diabetes = fields.Boolean('Diabetes')
    mental = fields.Boolean('Mental')
    # disorders = fields.Boolean('Disorders')
    stroke = fields.Boolean('Stroke')
    TB = fields.Boolean('TB')
    HTN_other = fields.Char(string='Others_Specify')
    medicine_or_drugs = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                         string='Is your child allergic to any medicine/drugs?')
    medicine_or_drugs_details = fields.Char(string='If yes, please indicate the name of the medicine/drug')
    give_consent_oral_analgesic = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                   string = 'A) I give consent to the School Nurse to give my child oral analgesic or any antipyretic drug (for pain and administer first aid, if needed')
    give_consent_hospital_treatment = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                       string='B) I give my consent for emergency measure including hospital treatment to be initiated for my child incase an accident or sudden illness (including school planned excursions)')
    give_consent_immunization = fields.Selection([('yes', 'YES'), ('no', 'NO')],
                                                 string='I give consent for the immunization for my child (applicable to children being admitted in Grade 1 and above')

    @api.onchange('special_learning_disability')
    def onchange_special_learning_disability(self):
        if not self.special_learning_disability:
            self.special_learning_disability_details = False

    @api.multi
    def write(self, vals):
        """
        overide write method,
        parent data synk with it's all child,
        student data synk with registration object.
        -------------------------------------------
        :param vals:
        :return:
        """
        for rec in self:
            if rec.is_parent:
                child_vals = {}
                field_list = ['father_nationality','father_passport','father_emirates_id','parent_address',
                              'mother_nationality','mother_passport','mother_emirates_id','spe_contribution',
                              'special_contribution_any_other']
                for key in field_list:
                    if vals.get(key):
                        child_vals.update({key : vals.get(key)})
                if vals.get('parents_office_contact'):
                    child_vals.update({'parent_office_contact' : vals.get('parents_office_contact')})
                for child in rec.chield1_ids:
                    child.write(child_vals)
        return super(PaperLessStudent, self).write(vals)