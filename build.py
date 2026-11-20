"""Build data.js for the site: the two fake Smartsheet logs, the dictionary rows and where each one is on a HubSpot screenshot.

    python -I build.py

The dictionary text comes from the HubSpot project (scripts/smartsheet_dictionary.py); sheets.json holds the fake rows
(no real patient). Rectangles are x, y, width, height in pixels on the 1568 x 726 screenshots in img/.
TASKS (below the dictionary rows) are the "How do I..." walkthroughs of the second mode.
"""
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, r'E:\CodeX\hubspot-ict-cm\scripts')
import smartsheet_dictionary as d  # noqa: E402

SCREENS = [
    ('new-patient', 'New ICT Patient page', 'Create the patient'),
    ('overview-1', 'Patient page: Overview tab, Next Step and the Case box', 'Open the patient'),
    ('overview-casetype', 'Overview tab: the Case Type list', 'Overview'),
    ('overview-2', 'Overview tab: Last Contact, Letters, Where each team stands', 'Open the patient'),
    ('overview-3', 'Overview tab: Medical Follow-up, and the left card', 'Open the patient'),
    ('overview-4', 'Overview tab: Liens and Care, Medical Follow-up', 'Open the patient'),
    ('whats-left', 'Engagement Steps: What\'s Left', 'Overview'),
    ('demographics-1', 'Patient Demographics tab: Patient', 'Patient Demographics'),
    ('demographics-2', 'Patient Demographics tab: Contact and Address', 'Patient Demographics'),
    ('demographics-3', 'Patient Demographics tab: Emergency Contacts, Parent / Guardian', 'Patient Demographics'),
    ('ed-notes', 'Hospital EMR tab: ED Visit and its notes (first on the tab)', 'Hospital EMR'),
    ('ed-notes-hpi', 'Hospital EMR tab: ED Visit Notes, HPI Notes', 'Hospital EMR'),
    ('ed-visit', 'Hospital EMR tab: ED Visit, Visit', 'Hospital EMR'),
    ('tracker-1', 'Hospital EMR tab: Hospital EMR Tracker, H2 and H3', 'Hospital EMR'),
    ('tracker-mid', 'Hospital EMR Tracker: H2 dates, H4, H5, H6, H7', 'Hospital EMR'),
    ('tracker-2', 'Hospital EMR Tracker: Completed (1): H1, BI Added Date', 'Hospital EMR'),
    ('tracker-3', 'Hospital EMR Tracker: closing the account', 'Hospital EMR'),
    ('log-call', 'Log a Call', 'Calls'),
    ('log-call-outcome', 'Log a Call: the Call outcome list', 'Calls'),
    ('insurance-top', 'Insurance and Verification tab: Case Documents', 'Insurance'),
    ('insurance-coverage-type', 'Insurance card: New Insurance, Coverage Type', 'Insurance'),
    ('insurance-form', 'Insurance card: New Insurance', 'Insurance'),
    ('insurance-form-save', 'Insurance card: New Insurance, Save Insurance', 'Insurance'),
    ('insurance-policy', 'Payer Order: the first policy', 'Insurance'),
    ('insurance-second', 'Payer Order: the second policy', 'Insurance'),
    ('insurance-moveup', 'Payer Order: Move Up', 'Insurance'),
    ('insurance-moved', 'Payer Order: after Move Up', 'Insurance'),
    ('insurance-verify', 'Insurance card: Verify a policy', 'Insurance'),
    ('insurance-verify-result', 'Verify: the Result list', 'Insurance'),
    ('insurance-verify-failed', 'Verify: a failed result needs a note', 'Insurance'),
    ('insurance-notpl', 'Insurance tab: No TPL / No Case Confirmation', 'Insurance'),
    ('insurance-notpl-form', 'Insurance tab: Confirm No TPL / No Case', 'Insurance'),
    ('insurance-notpl-reason', 'Confirm No TPL / No Case: the Reason list', 'Insurance'),
    ('attorney-top', 'Patient Attorney tab', 'Attorney'),
    ('attorney-status', 'Patient Attorney tab: the Attorney Status list', 'Attorney'),
    ('attorney-form', 'Attorneys card: New Attorney', 'Attorney'),
    ('attorney-form-save', 'Attorneys card: New Attorney, Save Attorney', 'Attorney'),
    ('attorney-current', 'Attorneys card: Current Patient Attorney', 'Attorney'),
    ('attorney-verify', 'Attorneys card: Add New Verification', 'Attorney'),
    ('attorney-verify-method', 'Add New Verification: the Verification Method list', 'Attorney'),
    ('attorney-verify-result', 'Add New Verification: the Result list', 'Attorney'),
    ('lien-top', 'Lien and Collection tab', 'Lien'),
    ('lien-form', 'Lien and Collection tab: New Lien', 'Lien'),
    ('patients-list', 'ICT Patients list', 'Open the patient'),
    ('tabs-more', 'Patient page: the More tabs', 'Open the patient'),
    ('activities-menu', 'Patient page: Add activities', 'Calls'),
]

# Rectangles are [x, y, width, height] in pixels of the 1568 x 726 screenshots (retaken 2026-11-18).
CASE_TYPE = ('overview-1', [572, 485, 270, 44], 'Case Type (Overview tab, Case box)')
DATE_OF_INJURY = ('overview-1', [572, 540, 270, 44], 'Date of Injury (Overview tab, Case box)')
ADD_INSURANCE = ('insurance-top', [633, 597, 117, 31], '+ Add Insurance')
STAGE = ('overview-1', [233, 377, 150, 36], 'Stage')
NO_TPL = ('insurance-notpl', [554, 439, 612, 100], 'No TPL / No Case Confirmation')
STATUS = ('attorney-top', [571, 343, 190, 40], 'Attorney Status')
CARE = ('overview-4', [554, 499, 612, 82], 'Liens and Care: the Care Coordination record')
APPOINTMENT = ('overview-3', [581, 368, 575, 250], 'Initial Appointment')
INJURY = ('ed-visit', [571, 346, 590, 72], 'Incident Type, Injured Body Parts, Other Injury Notes')
CLOSE = ('tracker-3', [554, 458, 612, 250], 'No TPL Discovered: Close the Account')
OUTCOME = ('log-call', [1008, 315, 125, 48], 'Call outcome')
LAST_CONTACT = ('overview-2', [556, 203, 298, 167], 'Last Contact')
CALL_NOTES = ('log-call', [927, 450, 490, 55], 'The notes of the call')
COVER_HEALTH = ('insurance-coverage-type', [573, 516, 570, 32], 'Health Insurance (in the Coverage Type list)')
COVER_MEDPAY = ('insurance-coverage-type', [573, 484, 570, 32], 'MedPay (in the Coverage Type list)')

TARGETS = {
    'Date / Intake DATE': [('overview-3', [233, 432, 200, 40], 'ICT Intake Date'), ('ed-visit', [772, 431, 190, 38], 'ICT Intake Date')],
    'LAST NAME (GUARDIAN)': [('new-patient', [532, 197, 170, 53], 'Last Name'), ('demographics-1', [974, 304, 180, 36], 'Last Name'),
                             ('demographics-3', [555, 449, 611, 231], 'Parent / Guardian (for a patient under 18)')],
    'FIRST NAME': [('new-patient', [352, 197, 170, 53], 'First Name'), ('demographics-1', [571, 304, 190, 36], 'First Name')],
    'DOB': [('new-patient', [352, 338, 190, 53], 'Date of Birth'), ('demographics-1', [571, 417, 190, 36], 'Date of Birth')],
    'Language / LANGUAGE': [('new-patient', [352, 408, 97, 53], 'Patient Language'), ('demographics-1', [974, 417, 180, 36], 'Patient Language'),
                            ('demographics-1', [571, 474, 190, 36], 'Interpreter Needed')],
    'PHONE': [('new-patient', [352, 267, 170, 53], 'Phone Number'), ('demographics-2', [573, 200, 270, 93], 'Phone Number, Secondary Phone Number')],
    'Additional Contact Info': [('demographics-3', [555, 227, 611, 201], 'Emergency Contacts'), ('demographics-3', [555, 449, 611, 231], 'Parent / Guardian')],
    'ADDRESS': [('demographics-2', [866, 145, 298, 410], 'Address')],
    'EMAIL': [('demographics-2', [573, 314, 270, 36], 'Email')],
    'MRN': [('new-patient', [352, 478, 170, 53], 'MRN'), ('ed-notes', [571, 571, 190, 38], 'MRN')],
    'Account Number': [('new-patient', [532, 478, 170, 53], 'Hospital Account Number'), ('ed-notes', [772, 571, 190, 38], 'Hospital Account Number')],
    'HPH ER': [('new-patient', [459, 408, 170, 53], 'Hospital Facility'), ('ed-visit', [571, 292, 190, 38], 'Hospital Facility')],
    'Patient Engagement Specialist': [('overview-1', [881, 465, 200, 40], 'Owner')],
    'Date Of Injury (DOI)': [('ed-visit', [974, 292, 180, 38], 'Date of Injury'), DATE_OF_INJURY],
    '(new) Date of Service (DOS)': [('new-patient', [352, 549, 190, 53], 'Date of Service (DOS)'), ('ed-visit', [772, 292, 190, 38], 'Date of Service (DOS)')],
    'BIBA': [('ed-visit', [571, 432, 190, 38], 'BIBA')],
    'Chief Complaint / CHIEF COMPLAINT': [INJURY],
    'Provider Notes': [('ed-notes-hpi', [569, 325, 575, 191], "HPI Notes: the doctor's notes, in ED Visit Notes")],
    'DETAIL/ADMISSION STATUS': [('ed-notes', [554, 245, 612, 253], 'What the hospital wrote: ED Visit Notes'),
                                ('log-call', [927, 450, 490, 55], 'What the patient told us: the notes of the call'), CASE_TYPE],
    'ED visit charges ($)': [('ed-visit', [974, 432, 180, 38], 'ER Bill Amount')],
    'INTAKE/TIME TO CALL': [('overview-2', [572, 306, 270, 42], 'Callback Time, under Last Contact: click it and pick the day and time'),
                            ('log-call', [927, 579, 380, 26], 'A follow-up task: its time is the Callback Time')],
    'INTAKE TIMESTAMP': [('overview-1', [1257, 377, 243, 108], 'Created: recorded by the system')],
    'LINK TO PATIENT FILES': [('overview-1', [554, 358, 612, 62], 'All Files'), ('insurance-top', [572, 416, 270, 112], 'Police / Crash Report, Case Files')],
    'Came Back to ER': [('new-patient', [352, 549, 190, 53], 'A new patient with the new DOS')],
    'Lead Owner': [('overview-1', [881, 465, 200, 40], 'Owner')],
    'Calling Team Agent': [('overview-2', [556, 203, 298, 167], 'Last Contact: who called')],
    'CONTACT DATE': [('overview-2', [556, 203, 298, 167], 'Last Contact: when, and how many attempts'), ('log-call', [927, 373, 172, 56], 'Activity date')],
    'Case Management DETAILS': [CALL_NOTES, ('overview-1', [1217, 93, 306, 415], 'Notes and Calls')],
    'LTM/LVM': [OUTCOME],
    'No Answer/ No contact': [OUTCOME],
    'NO CALL/Pt REFUSED': [STAGE],
    'PI': [CASE_TYPE], 'WC': [CASE_TYPE], 'Maybe TPL': [CASE_TYPE], 'At fault Drivers': [CASE_TYPE],
    'NO TPL/NO CASE': [CASE_TYPE, NO_TPL],
    'Not finalised/Unclear TPL Status': [CASE_TYPE],
    'Referral Case': [STATUS],
    'Lost Case': [STAGE],
    'Private health insurance': [ADD_INSURANCE, COVER_HEALTH],
    'Commercial insurance': [ADD_INSURANCE],
    'Nursing Home': [INJURY],
    'School/Sports injury': [INJURY],
    'Union WC': [CASE_TYPE, ADD_INSURANCE],
    'Federal WC': [CASE_TYPE, ADD_INSURANCE],
    'Insurance / Responsible Payer': [('insurance-form', [555, 247, 611, 458], 'New Insurance: one box per fact'),
                                      ('insurance-policy', [555, 139, 611, 330], 'The saved policy, first in the Payer Order'),
                                      ('insurance-top', [572, 304, 270, 170], 'Police Report Number, Police Department, Police / Crash Report')],
    'Health insurance carrier': [ADD_INSURANCE, COVER_HEALTH],
    'MedPay/ UIM': [ADD_INSURANCE, COVER_MEDPAY],
    'TPL Insurance confirmed': [('insurance-verify', [572, 210, 572, 445], 'Verify'), ('insurance-policy', [632, 190, 62, 22], 'Verified')],
    'Insurance Info Last Update Timestamp': [('insurance-policy', [572, 428, 420, 40], 'Added On, Last Verified On')],
    'Insurance Team Agent': [('insurance-policy', [572, 486, 400, 24], 'Verification line: who verified, and when')],
    'Insurance added to EZDocs': [('tracker-1', [574, 389, 270, 40], 'TPL/WC Insurance Added to Hospital Date')],
    'AgreeD to speak to IN network Atty': [STATUS],
    'Referral Timestamp / ATTY Referral Date': [('attorney-top', [772, 343, 190, 40], 'Referred to Attorney Date')],
    "Attorney's Detail": [('attorney-form', [572, 222, 572, 152], 'Attorney Name, Law Firm'), ('attorney-top', [554, 478, 612, 248], 'Current Patient Attorney')],
    'Attorney Contact Details': [('attorney-form', [572, 478, 572, 248], 'Phone, Fax, Email, Address')],
    "Agreement sent/ PT's not sent back yet": [('attorney-top', [772, 343, 382, 40], 'Referred date filled, Signed date still empty')],
    'Signed with Atty; Signing Date with IN-N Atty': [('attorney-top', [974, 343, 180, 40], 'Attorney Signed Date')],
    'Attorney Declined Case': [('attorney-top', [571, 399, 190, 40], 'Attorney Rejected Date')],
    'Patient has own Atty': [STATUS],
    'Own Attorney; Own Law-Firm; Own Atty/Law-Firm Detail': [('attorney-form', [572, 143, 572, 583], 'New Attorney')],
    'Signed with OUT-N Atty': [('attorney-verify', [572, 371, 572, 305], 'Add New Verification'), ('attorney-top', [573, 566, 133, 22], 'Representing (Verified)')],
    'Needs Appt': [('overview-3', [581, 232, 190, 40], 'Medical Follow-up')],
    'Appt Scheduled': [APPOINTMENT],
    'Appt Location': [('overview-3', [581, 317, 575, 40], 'Medical Follow-up Destination, Provider Name and Location')],
    'Medical Appt Details': [APPOINTMENT, ('overview-3', [776, 232, 190, 40], 'Medical Follow-up Note')],
    'Medical Follow-up Details': [CARE],
    'Scheduled Extra Appointment; Details Of EA': [CARE],
    'Referred Back To HPH / NM': [('overview-3', [581, 317, 280, 40], 'Medical Follow-up Destination')],
    'Accepted By HPH / NWM': [APPOINTMENT],
    'Added to Nimbly': [('overview-3', [233, 620, 260, 58], 'Nimbly Patient Link')],
    'Billing Indicator Added to HPH / EPIC': [('tracker-1', [556, 210, 52, 22], 'H1 BI'), ('tracker-2', [576, 601, 590, 115], 'H1 BI: BI Added Date (under Completed)'),
                                              ('overview-3', [233, 574, 200, 40], 'BI Added Date')],
    'Billing Added To EPIC': [('tracker-1', [556, 282, 297, 280], 'H2 Coverage Added to Hospital EMR')],
    'Atty info added to Epic': [('tracker-1', [556, 282, 297, 280], 'H2: Patient Attorney Added to Hospital Date')],
    'No Discovery - Closed after 30 days': [CLOSE, ('tracker-1', [553, 169, 170, 22], 'The hospital deadline')],
    'Account Closed': [CLOSE],
    'MR & BILLING SENT; MR & BILLING DETAILS': [('tracker-mid', [866, 325, 297, 196], 'H5 Medical Records and Bill (MR&B)')],
    '(new) Liens, hospital bills and payments': [('tracker-mid', [558, 325, 297, 196], 'H4 Lien: made on the Lien and Collection tab'),
                                                 ('lien-top', [554, 283, 624, 122], 'Lien and Collection: Liens, Hospital Bills')],
}


# ---- The walkthrough (user, 2026-11-16: "walk through 是从点进那个病人开始"): the ICT Patients list, the patient, the tab,
# the click that opens a form, then the field. A field typed when the patient is created comes last, on the New ICT Patient page.
LIST_STEP = ('patients-list', [276, 289, 142, 26], "Open ICT Patients in the left menu and click the patient's name.")
IN_ROW = ' (On a narrow screen it can be under More.)'
UNDER_MORE = ' (On a wide screen it can be in the row itself.)'
TAB_STEP = {
    'Overview': ('overview-1', [534, 93, 152, 38],
                 'The patient page opens. Click the Overview tab. If another tab is showing and Overview is not in the row, click More, then Overview.'),
    'Hospital EMR': ('tabs-more', [960, 150, 150, 26], 'On the patient page, click More, then Hospital EMR.' + UNDER_MORE),
    'Patient Demographics': ('tabs-more', [960, 183, 150, 26], 'On the patient page, click More, then Patient Demographics.' + UNDER_MORE),
    'Insurance and Verification': ('overview-1', [687, 93, 188, 38], 'On the patient page, click the Insurance and Verification tab.' + IN_ROW),
    'Patient Attorney': ('overview-1', [877, 93, 149, 38], 'On the patient page, click the Patient Attorney tab.' + IN_ROW),
    'Lien and Collection': ('tabs-more', [960, 248, 150, 26], 'On the patient page, click More, then Lien and Collection.' + UNDER_MORE),
    'Log a Call': ('activities-menu', [1305, 281, 190, 26],
                   'On the patient page, click Add activities, then Log a call. (The Call button under the patient name does the same.)'),
}
TAB_OF = {'overview': 'Overview', 'demographics': 'Patient Demographics', 'ed': 'Hospital EMR', 'tracker': 'Hospital EMR',
          'insurance': 'Insurance and Verification', 'attorney': 'Patient Attorney', 'lien': 'Lien and Collection', 'log': 'Log a Call'}
BEFORE = {
    'insurance-form': ('insurance-top', [633, 597, 117, 31], 'Click + Add Insurance and pick the Coverage Type.'),
    'insurance-verify': ('insurance-policy', [572, 600, 60, 32], 'On the policy, click Verify.'),
    'attorney-form': ('attorney-top', [635, 243, 112, 30], 'Click + Add Attorney.'),
    'attorney-verify': ('attorney-current', [571, 607, 145, 32], 'On the current attorney, click Add New Verification.'),
}


# ---- Part A: "How do I..." tasks, independent of the Smartsheet columns (2026-11-18).
# One step = one screenshot, one rectangle, one short sentence (and an optional line of extra help).
# (screen, [x, y, w, h], sentence, kind[, extra help]); kinds: look, tab, click, pick, type, save, field.
OVERVIEW_TAB = ('overview-1', [534, 93, 152, 38], 'Click the Overview tab.', 'tab',
                'If Overview is not in the row of tabs, click More, then Overview.')
HOSPITAL_TAB = ('tabs-more', [960, 150, 150, 26], 'Click More, then Hospital EMR.', 'tab',
                'If Hospital EMR is already in the row of tabs, just click it.')
INSURANCE_TAB = ('overview-1', [687, 93, 188, 38], 'Click the Insurance and Verification tab.', 'tab',
                 'If it is not in the row of tabs, click More, then Insurance and Verification.')
ATTORNEY_TAB = ('overview-1', [877, 93, 149, 38], 'Click the Patient Attorney tab.', 'tab',
                'If it is not in the row of tabs, click More, then Patient Attorney.')
LIEN_TAB = ('tabs-more', [960, 248, 150, 26], 'Click More, then Lien and Collection.', 'tab',
            'If Lien and Collection is already in the row of tabs, just click it.')

TASKS = [
    {'slug': 'find-hidden-tab', 'title': 'Find a tab that is under More',
     'about': 'Hospital EMR, Patient Demographics, Activities and Lien and Collection are not in the row of tabs.',
     'words': 'tab hidden more where is hospital emr demographics activities lien collection insurance attorney',
     'steps': [
         ('overview-1', [534, 93, 578, 38], 'Look at the row of tabs on the patient page: Overview, Insurance and Verification, Patient Attorney.', 'look',
          'The tabs you do not see here are under More.'),
         ('overview-1', [1027, 93, 85, 38], 'Click More, to the right of the tabs.', 'click'),
         ('tabs-more', [960, 150, 150, 26], 'Hospital EMR: the ED Visit and the Hospital EMR Tracker.', 'tab'),
         ('tabs-more', [960, 183, 150, 26], 'Patient Demographics: the patient, contact and address.', 'tab'),
         ('tabs-more', [960, 248, 150, 26], 'Lien and Collection: the liens and the hospital bills.', 'tab',
          'The tab you open moves into the row, so the next time More may list other tabs (for example Overview).'),
     ]},
    {'slug': 'case-type-and-injury-date', 'title': 'Pick the Case Type and Date of Injury',
     'about': 'Both are in the Case box on the Overview tab. They save at once.',
     'words': 'case type pi wc possible tpl unknown date of injury doi overview case box',
     'steps': [
         OVERVIEW_TAB,
         ('overview-1', [556, 443, 298, 158], 'Find the Case box. It has Case Type and Date of Injury.', 'look'),
         ('overview-1', [572, 485, 270, 44], 'Click Case Type.', 'click'),
         ('overview-casetype', [573, 267, 262, 230], 'Pick the Case Type from the list, for example PI, WC, PI and WC or Possible TPL.', 'pick',
          'Pick the final Case Type as soon as you know it. Possible TPL means it is still being checked. Unknown is not proof of no coverage.'),
         ('overview-1', [572, 540, 270, 44], 'Click Date of Injury and pick the day.', 'field'),
         ('insurance-top', [572, 247, 270, 48], 'The Insurance and Verification tab shows the Case Type but you do not change it there. It says: Change it on the Overview tab (Case box).',
          'look'),
     ]},
    {'slug': 'add-insurance', 'title': 'Add an insurance',
     'about': 'A new policy goes to the end of the Payer Order list on the Insurance and Verification tab.',
     'words': 'add insurance policy coverage type insurance company claim number policy number third-party liability workers compensation own auto medpay health',
     'steps': [
         INSURANCE_TAB,
         ('insurance-top', [633, 597, 117, 31], 'Click + Add Insurance.', 'click'),
         ('insurance-coverage-type', [573, 384, 570, 180], 'Pick the Coverage Type.', 'pick',
          "Third-Party Liability (TPL) is the other party's insurer. Workers' Compensation (WC) is for a work injury. Own Auto / Vehicle Insurance is the patient's own auto policy."),
         ('insurance-form', [572, 402, 572, 70], 'In Insurance Company, type part of the name and pick it from the list.', 'type',
          'A name that is not in the list becomes a Company when you save.'),
         ('insurance-form', [572, 496, 352, 56], 'Fill in the Claim Number. Add the Policy Number if you have it.', 'type',
          'Whose Policy, Insurance Holder Name, the adjuster and the Billing Address are optional.'),
         ('insurance-form-save', [572, 542, 126, 34], 'Click Save Insurance.', 'save'),
         ('insurance-second', [572, 385, 272, 24], 'The new policy is in the Payer Order list. It says Not Verified.', 'look',
          'What the patient tells you is not a verification. Call the insurance company, then click Verify on the policy.'),
     ]},
    {'slug': 'verify-insurance', 'title': 'Verify an insurance policy',
     'about': 'After you call the insurance company. Each policy is verified on its own.',
     'words': 'verify verification method result verified attempt to verify failed wrong info phone reference confirmation number',
     'steps': [
         INSURANCE_TAB,
         ('insurance-policy', [572, 600, 60, 32], 'Find the policy in the Payer Order list and click Verify on it.', 'click'),
         ('insurance-verify', [572, 252, 572, 56], 'Pick the Verification Method, for example Phone.', 'pick',
          'Call the insurance company first. What the patient tells you is not a verification.'),
         ('insurance-verify', [572, 321, 572, 126], 'Add the number you called and a Reference / Confirmation Number if you like.', 'type',
          'Only the Verification Method and the Result are required.'),
         ('insurance-verify', [572, 462, 572, 56], 'Leave Result on Verified.', 'pick'),
         ('insurance-verify', [572, 617, 138, 34], 'Click Save Verification. The policy shows Verified.', 'save',
          'Your name and the time are recorded by the system.'),
         ('insurance-verify-result', [573, 470, 570, 128], 'If the insurance company says the claim is not the patient\'s, pick Attempt to Verify Failed (Wrong Info) as the Result.', 'pick'),
         ('insurance-verify-failed', [572, 532, 572, 78], 'Write what was wrong in Notes: What Was Wrong (Required). Then click Save Verification.', 'type',
          'The policy then shows Verification Failed and does not count. Click Edit to correct it, then verify again.'),
     ]},
    {'slug': 'change-payer-order', 'title': 'Change which insurance is billed first',
     'about': 'The Payer Order list on the Insurance and Verification tab is in the order the policies are billed.',
     'words': 'payer order primary secondary move up move down billed first order insurance',
     'steps': [
         INSURANCE_TAB,
         ('insurance-policy', [573, 190, 120, 22], 'In Payer Order the top policy is tagged Primary. The next one is Secondary.', 'look'),
         ('insurance-policy', [701, 600, 106, 32], 'Click Move Down on a policy to move it down.', 'click',
          'Nothing reorders the list by itself. Every move is kept in the history.'),
         ('insurance-moveup', [701, 198, 92, 32], 'Click Move Up on a policy to move it up.', 'click'),
         ('insurance-moved', [554, 160, 612, 52], 'A green message says what changed, for example Progressive is now Primary.', 'look',
          "With two policies of one type, the higher one is that type's Primary: the case verification looks at it."),
     ]},
    {'slug': 'confirm-no-tpl-no-case', 'title': 'Confirm No TPL / No Case',
     'about': 'When there is no insurance and no case. It is one button.',
     'words': 'no tpl no case confirm confirmation undo reason hospital close account billing indicator',
     'steps': [
         ('overview-1', [572, 485, 270, 44], 'Overview tab, Case box: click Case Type and pick No TPL / No Case.', 'pick',
          'The button Confirm No TPL / No Case then shows in the same box. (It is not in this picture because this patient is not set to No TPL / No Case.)'),
         INSURANCE_TAB,
         ('insurance-notpl', [571, 494, 174, 26], 'Or click Confirm No TPL / No Case at the bottom of the Insurance and Verification tab.', 'click'),
         ('insurance-notpl-reason', [589, 574, 536, 142], 'Pick the Reason: No Case, No Response, TPL Case: No Coverage or Patient at Fault: No MedPay.', 'pick'),
         ('insurance-notpl-form', [588, 680, 174, 28], 'Add a note if you like. Click Confirm No TPL / No Case.', 'save',
          'Today\'s date and your name are recorded. The hospital team is told to remove the billing indicator and close the account. The Case Type is then locked.'),
         ('insurance-notpl', [554, 439, 612, 100], 'To undo it, click Undo Confirmation in this box at the bottom of the Insurance and Verification tab.', 'look',
          'Use it if it was a mistake or a payer was found after all. Only then can the Case Type be changed. (The button shows only once No TPL / No Case is confirmed, so it is not in this picture.)'),
     ]},
    {'slug': 'attorney', 'title': 'Set Attorney Status, add the attorney and verify',
     'about': 'All on the Patient Attorney tab.',
     'words': 'attorney status own attorney referred declined wants referral undecided add attorney law firm verify representing add new verification',
     'steps': [
         ATTORNEY_TAB,
         ('attorney-top', [571, 343, 190, 40], 'Under Does the Patient Have an Attorney?, click Attorney Status.', 'click'),
         ('attorney-status', [572, 388, 170, 180], 'Pick the status: Own Attorney, Referred to Attorney, Declined Attorney, Wants Referral or Undecided.', 'pick',
          'The dates that fit the status show next to it: Referred to Attorney Date, Attorney Signed Date, Attorney Rejected Date.'),
         ('attorney-top', [635, 243, 112, 30], 'Click + Add Attorney.', 'click'),
         ('attorney-form', [572, 143, 572, 56], 'Pick the Role. The patient\'s own lawyer is the Current Patient Attorney.', 'pick',
          'This test patient already has a current attorney, so this picture lists only Previous Attorney on This Case and Defense Attorney (Insurance Side). To change the current attorney use Replace Attorney.'),
         ('attorney-form', [572, 223, 572, 150], 'Type the Attorney Name (required) and pick the Law Firm.', 'type',
          'A law firm that is not in the list becomes a Company when you save.'),
         ('attorney-form', [572, 478, 572, 60], 'Add the Phone, and the Fax or Email if you have them.', 'type'),
         ('attorney-form-save', [572, 443, 122, 34], 'Click Save Attorney.', 'save'),
         ('attorney-current', [571, 607, 145, 32], 'After you call the law office, click Add New Verification on the attorney.', 'click'),
         ('attorney-verify-method', [573, 470, 570, 142], 'Pick the Verification Method: Phone, Email, Written Confirmation or Other.', 'pick'),
         ('attorney-verify-result', [573, 528, 570, 112], 'Pick the Result: Representing, Not Representing or Attempt to Verify Failed (Wrong Info).', 'pick',
          'A failed attempt needs a note saying what was wrong.'),
         ('attorney-verify', [572, 636, 138, 32], 'Click Save Verification. The attorney shows Representing (Verified).', 'save'),
     ]},
    {'slug': 'log-call', 'title': 'Log a call',
     'about': 'Every call is logged with its Call outcome.',
     'words': 'call log a call outcome no answer voicemail connected wrong number follow up task callback',
     'steps': [
         ('activities-menu', [1332, 160, 85, 28], 'On the right side, click Add activities.', 'click'),
         ('activities-menu', [1305, 281, 190, 26], 'Click Log a call.', 'click', 'The Call button under the patient name also logs a call.'),
         ('log-call', [1008, 315, 125, 48], 'Click Call outcome.', 'click',
          'A call saved without a Call outcome is not counted.'),
         ('log-call-outcome', [1010, 382, 160, 222], 'Pick the outcome. No answer if nobody picked up, Left voicemail if you left one, Connected if you spoke with the patient.', 'pick'),
         ('log-call', [927, 450, 490, 55], 'Write a short note about the call.', 'type'),
         ('log-call', [927, 579, 380, 26], 'To call back later, tick Create a To-do task to follow up and pick the day and time.', 'click',
          'The time shows as Callback Time on the Overview tab, under Last Contact. You can also set it there directly.'),
         ('log-call', [927, 626, 82, 32], 'Click Log call.', 'save',
          'Within a few seconds the Call Team box on the Overview tab shows the call.'),
     ]},
    {'slug': 'hospital-dates', 'title': 'Enter the hospital dates',
     'about': 'On the Hospital EMR tab: read the ED Visit, then enter the dates in the Hospital EMR Tracker.',
     'words': 'hospital emr ed visit notes triage hpi discharge tracker h1 bi added date h2 tpl wc insurance added to hospital date attorney added billing indicator',
     'steps': [
         HOSPITAL_TAB,
         ('ed-notes', [554, 245, 612, 253], 'The ED Visit is first on the tab, and its ED Visit Notes come first: Triage Notes, HPI Notes, Discharge Notes.', 'look',
          'Click a note tab to read the whole note.'),
         ('ed-notes-hpi', [763, 265, 190, 102], 'HPI Notes are the doctor\'s notes (History of Present Illness). Triage Notes are the nurse\'s notes.', 'look'),
         ('ed-visit', [554, 232, 612, 255], 'Under the notes: Hospital Facility, Date of Service (DOS), Date of Injury, Incident Type, BIBA, ICT Intake Date, ER Bill Amount.', 'look',
          'Click a value to change it. It saves at once.'),
         ('tracker-1', [557, 210, 508, 22], 'The Hospital EMR Tracker has one chip for each step, H1 to H7.', 'look'),
         ('tracker-2', [576, 601, 590, 115], 'H1 BI (Billing Indicator): enter BI Added Date, the day the billing indicator was added in the hospital EMR.', 'field',
          'When H1 is done it folds into Completed (1): H1. Click that line to open it.'),
         ('tracker-1', [574, 389, 270, 40], 'H2 Coverage Added to Hospital EMR: click TPL/WC Insurance Added to Hospital Date and pick the day.', 'field',
          'It saves by itself. The date is the tick.'),
         ('tracker-mid', [574, 199, 270, 40], 'When the patient attorney is verified, enter Patient Attorney Added to Hospital Date the same way.', 'field',
          'Patient Own Auto Insurance Added to Hospital Date is for a verified own auto policy.'),
     ]},
    {'slug': 'create-lien', 'title': 'Create a lien',
     'about': 'On the Lien and Collection tab, once the insurance is verified.',
     'words': 'lien create send the lien to attach bills lien letter confirm and create lien hospital bill',
     'steps': [
         LIEN_TAB,
         ('lien-top', [570, 335, 95, 26], 'Under Liens, click + Create Lien.', 'click',
          'If there is no hospital bill yet, click + Add Hospital Bill first.'),
         ('lien-form', [588, 423, 538, 56], 'Pick who the lien goes to in Send the Lien To.', 'pick',
          'The insurer is offered only when the policy is verified and has a claim number and a full billing address. Otherwise the form says what is missing.'),
         ('lien-form', [588, 527, 538, 50], 'Tick the bills the lien is for under Attach Bills.', 'pick'),
         ('lien-form', [588, 639, 180, 30], 'Click Confirm and Create Lien. Nothing is sent yet.', 'save'),
         ('lien-top', [554, 283, 624, 122], 'Then upload the Lien Letter on that lien. The lien team sends it.', 'look'),
     ]},
    {'slug': 'next-step-and-whats-left', 'title': 'Read Next Step and What\'s Left',
     'about': 'They tell you what to do now and where to do it.',
     'words': 'next step whats left what to do now progress steps overview team boxes engagement',
     'steps': [
         OVERVIEW_TAB,
         ('overview-1', [554, 247, 612, 90], 'Next Step, the blue box at the top, says what to do now. It starts with where to go.', 'look',
          'For example: "Overview tab, Initial Appointment:". Once the patient is reached it can show an insurance line and an attorney line together, because the two do not wait for each other.'),
         ('overview-2', [556, 556, 609, 142], 'Where each team stands: Call Team, Insurance, Attorney and Hospital EMR, each with its steps and a progress bar.', 'look'),
         ('overview-2', [572, 656, 100, 26], 'Click What\'s Left to see every step.', 'click',
          'It is also in Reminders on the right side.'),
         ('whats-left', [817, 107, 714, 100], 'Still Needed lists each open step, with what to do and where.', 'look'),
         ('whats-left', [817, 236, 714, 340], 'Completed lists what is done, with the result.', 'look'),
     ]},
]


def walk(targets):
    page = [t for t in targets if t[0] != 'new-patient']
    steps, tab = [], None
    if page:
        steps.append(LIST_STEP + ('open',))
    for screen, rect, label in page:
        left = rect[0] < 520
        name = TAB_OF[screen.split('-')[0]]
        if not left and name != tab:
            steps.append(TAB_STEP[name] + ('tab',))
            tab = name
        if screen in BEFORE and BEFORE[screen] + ('click',) not in steps:
            steps.append(BEFORE[screen] + ('click',))
        steps.append((screen, rect, f'Here it is: {label}.' + (' It is on the left card, whichever tab is open.' if left else ''), 'field'))
    for screen, rect, label in targets:
        if screen == 'new-patient':
            steps.append((screen, rect, (f'For a new patient you type it first, on the New ICT Patient page: {label}.' if page
                                         else f'On the New ICT Patient page: {label}.'), 'create'))
    return [{'screen': a, 'rect': b, 'text': c, 'kind': k} for a, b, c, k in steps]


# Row colours as staff used them (the sheet's Color Keys column); the first rule that fits.
ROW_RULES = [('red', ['NO CALL/Pt REFUSED', 'NO TPL/NO CASE']), ('blue', ["Agreement sent/ PT's not sent back yet"]),
             ('green', ['AgreeD to speak to IN network Atty', 'Signed with Atty']), ('white', ['Patient has own Atty']),
             ('grey', ['LTM/LVM', 'No Answer/ No contact']), ('yellow', ['Appt Scheduled', 'Apoointment Scheduled']), ('pink', ['Needs Appt', 'NEEDS APPOINTMENT'])]


def row_colors(sheet):
    at = {h: i for i, h in enumerate(sheet['header'])}
    return [next((color for color, heads in ROW_RULES if any(h in at and row[at[h]] is True for h in heads)), 'white') for row in sheet['rows']]


def shift_dates(text, days=160):
    """The first fake patient's 2026 dates moved to the month of the HubSpot screenshots (the birth date stays)."""
    def moved(m, sep, order):
        a, b, y = m.group(1), m.group(2), m.group(3)
        if y not in ('26', '2026'):
            return m.group(0)
        day = datetime.date(2026, int(a), int(b)) + datetime.timedelta(days=days)
        pad = len(a) == 2
        return sep.join([f'{day.month:02d}' if pad else str(day.month), f'{day.day:02d}' if pad else str(day.day), str(day.year)[-len(y):]])
    text = re.sub(r'\b(\d{1,2})/(\d{1,2})/(\d{4}|\d{2})\b', lambda m: moved(m, '/', 0), text)
    return re.sub(r'\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b', lambda m: moved(m, '.', 0), text)


def letters(n):
    out = []
    for i in range(n):
        s, k = '', i
        while True:
            s = chr(65 + k % 26) + s
            k = k // 26 - 1
            if k < 0:
                break
        out.append(s)
    return out


def jpeg_size(path):
    """(width, height) of a JPEG, read from its header (no imaging library needed)."""
    with open(path, 'rb') as f:
        data = f.read()
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            return int.from_bytes(data[i + 7:i + 9], 'big'), int.from_bytes(data[i + 5:i + 7], 'big')
        i += 2 + int.from_bytes(data[i + 2:i + 4], 'big')
    raise ValueError(path)


TASK_KINDS = {'look', 'tab', 'click', 'pick', 'type', 'save', 'field'}


def build_tasks(sizes):
    slugs = [t['slug'] for t in TASKS]
    assert len(slugs) == len(set(slugs)), 'a task slug is used twice'
    out = []
    for t in TASKS:
        steps = []
        for st in t['steps']:
            screen, rect, text, kind = st[:4]
            assert kind in TASK_KINDS, (t['slug'], kind)
            assert screen in sizes, (t['slug'], screen)
            w, h = sizes[screen]
            x, y, rw, rh = rect
            assert x >= 0 and y >= 0 and rw > 0 and rh > 0 and x + rw <= w and y + rh <= h, (t['slug'], screen, rect, (w, h))
            steps.append({'screen': screen, 'rect': rect, 'text': text, 'kind': kind, 'help': st[4] if len(st) > 4 else ''})
        out.append({'slug': t['slug'], 'title': t['title'], 'about': t['about'], 'words': t['words'], 'steps': steps})
    return out


def main():
    sheets = json.load(open(os.path.join(HERE, 'sheets.json'), encoding='utf-8'))
    sheets['hph']['rows'][0] = [shift_dates(v) if isinstance(v, str) else v for v in sheets['hph']['rows'][0]]
    sheets['hph']['name'], sheets['nm']['name'] = 'Patient Intake (MAIN)', 'NM Patient Log'
    sheets['hph']['hospital'], sheets['nm']['hospital'] = 'Humboldt Park', 'Northwestern'
    for s in sheets.values():
        s['letters'] = letters(len(s['header']))
        s['rowColors'] = row_colors(s)
    columns, names = [], set()
    for group, rows in d.GROUPS:
        for name, hph, nm, was, where, how, kind in rows:
            names.add(name)
            columns.append({'id': len(columns), 'group': group, 'name': name.replace('(new) ', ''), 'isNew': name.startswith('(new)'),
                            'hph': [x.strip() for x in hph.split(',') if x.strip()], 'nm': [x.strip() for x in nm.split(',') if x.strip()],
                            'was': was, 'where': where, 'how': how, 'kind': kind,
                            'steps': walk(TARGETS.get(name, []))})
    assert not set(TARGETS) - names, set(TARGETS) - names
    screens = {s for s, _, _ in SCREENS}
    assert all(t['screen'] in screens for c in columns for t in c['steps'])
    sizes = {}
    for s, _, _ in SCREENS:
        path = os.path.join(HERE, 'img', s + '.jpg')
        assert os.path.exists(path), s
        sizes[s] = jpeg_size(path)
        assert sizes[s] == (1568, 726), (s, sizes[s])  # one size for every screenshot; index.html scales by the 1568 width
    unused = sorted(set(f[:-4] for f in os.listdir(os.path.join(HERE, 'img')) if f.endswith('.jpg')) - set(sizes))
    assert not unused, ('screenshots in img/ that are not listed in SCREENS', unused)
    for c in columns:
        for t in c['steps']:
            w, h = sizes[t['screen']]
            x, y, rw, rh = t['rect']
            assert 0 <= x and 0 <= y and x + rw <= w and y + rh <= h, (c['name'], t['screen'], t['rect'])
    tasks = build_tasks(sizes)
    data = {'sheets': sheets, 'columns': columns, 'tasks': tasks, 'screens': [{'id': s, 'title': t} for s, t, g in SCREENS]}
    with open(os.path.join(HERE, 'data.js'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('window.DATA = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n')
    print(len(columns), 'dictionary rows;', sum(1 for c in columns if c['steps']), 'with a walkthrough;', sum(len(c['steps']) for c in columns), 'steps;',
          len(SCREENS), 'screenshots;', len(tasks), 'tasks,', sum(len(t['steps']) for t in tasks), 'task steps')
    for name in ('MRN', 'Insurance / Responsible Payer', 'LTM/LVM', 'Added to Nimbly', 'Came Back to ER'):
        c = next(c for c in columns if c['name'] == name)
        print(' ', name, '->', ' | '.join(f"{s['kind']}:{s['screen']}" for s in c['steps']))
    print('row colours:', sheets['hph']['rowColors'], sheets['nm']['rowColors'])
    print('first fake patient:', [v for v in sheets['hph']['rows'][0][:20] if v != ''][:9])


if __name__ == '__main__':
    main()
