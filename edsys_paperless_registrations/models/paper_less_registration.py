from odoo import models, fields, api, _
from odoo.exceptions import except_orm

class PaperLessRegistration(models.Model):

    _inherit = 'registration'

    health_form_signed = fields.Boolean('Health form signed')
    postal_address = fields.Text('Postal Address')
    student_is_living_with = fields.Char('Student is living with')
    lang_spoken_at_home = fields.Many2many('res.lang',
                                               string='Language(s) spoken at home')
    english_is_spoken_at_home = fields.Selection([('yes','YES'),('no','NO')],
                                                 string="English is spoken at home (Yes / No)")
    english_written = fields.Selection([('none','None'),('some','Some'),
                                        ('satisfactory','Satisfactory'),
                                        ('proficient','Proficient')],string="Written")
    english_spoken = fields.Selection([('none','None'),('some','Some'),
                                       ('satisfactory','Satisfactory'),
                                       ('proficient','Proficient')],string="Spoken")
    english_reading = fields.Selection([('none','None'),('some','Some'),
                                        ('satisfactory','Satisfactory'),
                                        ('proficient','Proficient')],string="Reading")
    father_nationality = fields.Many2one('res.country',string="Father Nationality")
    father_passport = fields.Char('Father Passport')
    father_emirates_id = fields.Char('Father Emirates Id')
    father_designation = fields.Char('Father Designation')
    mother_nationality = fields.Many2one('res.country',string="Mother Nationality")
    mother_passport = fields.Char('Mother Passport')
    mother_emirates_id = fields.Char('Mother Emirates Id')
    mother_designation = fields.Char('Mother Designation')
    medium_of_instruction = fields.Char('Medium of Instruction')
    identified_gifted_or_talented = fields.Selection([('yes','YES'),('no','NO')],
                                                     string="Has your child ever been identified as gifted or talented ?")
    has_child_detained = fields.Selection([('yes','YES'),('no','NO')],
                                          string="Has your child ever been detained ?")
    has_child_detained_grade = fields.Many2one('course','Grade')
    child_received_academic_distinction = fields.Selection([('yes','YES'),('no','NO')],
                                                           string="Has your child received any academic distinction ?")
    child_received_academic_distinction_details = fields.Char(string='If yes, please indicate details')
    has_suspended_expelled_by_school = fields.Selection([('yes','YES'),('no','NO')],
                                                        string="Has your child ever been suspended/ expelled by any school in the past ?")
    has_suspended_expelled_by_school_details = fields.Char(string='If yes, please indicate details')
    child_associated_with_awareness = fields.Selection([('yes','YES'),('no','NO')],
                                                       string="Has your child been associated with any social awareness programme?")
    child_associated_with_awareness_details = fields.Char(string='If yes, please indicate details')
    member_of_environment_protection = fields.Selection([('yes','YES'),('no','NO')],
                                                        string="Has your child been a member of environment protection group ?")
    member_of_environment_protection_details = fields.Char(string='If yes, please indicate details')
    leadership_positions_in_school = fields.Selection([('yes','YES'),('no','NO')],
                                                      string="Has your child held any leadership positions in School? (Prefectorial Board/ Student Council)")
    leadership_positions_in_school_details = fields.Char(string='If yes, please indicate details')
    special_education_programme = fields.Selection([('yes','YES'),('no','NO')],
                                                   string="Has your child ever been in a speech therapy, remedial reading support, special education programme?")
    special_education_programme_details = fields.Char(string='If yes, please indicate details')
    special_learning_disability = fields.Selection([('yes','YES'),('no','NO')],
                                                   string="Has your child ever been identified as having a special learning disability?")
    special_learning_disability_details = fields.Selection([('reading','Reading'),('language','Language'),('mathematics','Mathematics')],
                                                           string="If yes, please indicate learning disability area")
    has_other_than_english_languages = fields.Selection([('yes','YES'),('no','NO')],
                                                        string="Has your child ever studied any languages other than English ?")
    other_than_english_languages = fields.Many2one('res.lang', 'If yes, please mention the other languages')
    hobbies_interests = fields.Text("Please list your child's hobbies / interests")
    has_play_any_musical_instrument = fields.Selection([('yes','YES'),('no','NO')],
                                                       string="Does your child play any musical instrument ?")
    musical_instrument_details = fields.Char(string='If yes, please specify')
    has_formal_training_in_music = fields.Selection([('yes','YES'),('no','NO')],
                                                    string="Has your child had any formal training in music ?")
    training_in_music_details = fields.Char(string='If yes, please give details')
    sport_child_play = fields.Char(string='Which sport does your child play ?')
    has_training_or_interest_art = fields.Selection([('yes','YES'),('no','NO')],
                                                    string="Has your child had any training / shown interest in fine arts ?")
    has_training_or_interest_art_details = fields.Char(string='If yes, please give details')
    inter_school_competitions = fields.Selection([('yes','YES'),('no','NO')],
                                                 string="Has your child participated in inter/ intra school competitions?")
    inter_school_competitions_details = fields.Char(string='If yes, please give details')
    special_activity_interested = fields.Char(string='Any other special activity your child is interested in?')

    adjusts_new_situations_with_ease = fields.Boolean('Adjusts to new situations with ease')
    has_small_group_of_friends = fields.Boolean('Has a small group of friends')
    has_never_adjust_new_situation = fields.Boolean('Has never had to adjust to a new situation')
    has_many_friends = fields.Boolean('Has many friends')
    likes_be_active_in_school = fields.Boolean('Likes to be active in school')
    expressions_describe_your_child = fields.Selection([('very_active','Very Active'),('very_quiet','Very Quiet'),
                                                        ('average','Average'),('above_average','Above Average'),
                                                        ('shy','Shy'),('sociable','Sociable'),
                                                        ('aggressive','Aggressive'),('other','Other')],
                                                       string='Please Select the expression that describe your child.')
    social_emotional_behavioural_difficulties = fields.Selection([('yes','YES'),('no','NO')],
                                                                 string="Has your child ever experienced social, emotional or behavioural difficulties?")
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
                                            string='Can the child button his shirt?')
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

    @api.multi
    def reminder_for_additional_form(self):
        if self.fee_structure_confirm != True:
             raise except_orm(_("Warning !"), _('Please Confirm the fee Structure before send reminder For Additional form'))
        return super(PaperLessRegistration,self).reminder_for_additional_form()

