"""Builds locale/mr/LC_MESSAGES/django.po (human-readable) and django.mo (binary,
loaded by Django at runtime) for the Marathi translations of LOKSETU's UI chrome.

No gettext/msgfmt binary is available in this environment, so django.mo is written
directly in pure Python using the standard GNU MO binary format, straight from the
TRANSLATIONS dict below (not by re-parsing the .po file, to avoid fragile parsing).
"""
import struct

TRANSLATIONS = {
    "About": "आमच्याबद्दल",
    "All Rights Reserved.": "सर्व हक्क राखीव.",
    "All categories": "सर्व प्रवर्ग",
    "All projects": "सर्व प्रकल्प",
    "All statuses": "सर्व स्थिती",
    "All tickets": "सर्व तिकिटे",
    "All types": "सर्व प्रकार",
    "All years": "सर्व वर्षे",
    "Allocated": "मंजूर निधी",
    "Avg. days to resolve": "निराकरणासाठी सरासरी दिवस",
    "Budget allocation and utilization for schemes and projects, by financial year.": "आर्थिक वर्षानुसार योजना व प्रकल्पांसाठीचा निधी वाटप आणि वापर.",
    "Budget": "अंदाजपत्रक",
    "Citizen\u2013Government Digital Bridge": "नागरिक\u2013शासन डिजिटल सेतू",
    "Complaint history": "तक्रार इतिहास",
    "Complaints by status": "स्थितीनुसार तक्रारी",
    "Complaints filed": "दाखल तक्रारी",
    "Complaints": "तक्रारी",
    "Connect with me:": "माझ्याशी संपर्क साधा:",
    "Contact support": "सहाय्यासाठी संपर्क",
    "Contact": "संपर्क",
    "Create account": "खाते तयार करा",
    "Dashboard": "डॅशबोर्ड",
    "Department": "विभाग",
    "Departments": "विभाग",
    "Developed by DEVJAYESH": "DEVJAYESH यांनी विकसित",
    "Disclaimer": "अस्वीकरण",
    "District": "जिल्हा",
    "Documents": "कागदपत्रे",
    "Download": "डाउनलोड करा",
    "Emergency numbers": "आपत्कालीन क्रमांक",
    "Emergency": "आपत्कालीन",
    "End date": "समाप्ती तारीख",
    "FAQ": "वारंवार विचारले जाणारे प्रश्न",
    "File a complaint": "तक्रार दाखल करा",
    "File your first complaint to see your status breakdown here.": "स्थिती पाहण्यासाठी येथे तुमची पहिली तक्रार दाखल करा.",
    "Filter": "गाळणी लावा",
    "For anything other than a civic complaint \u2014 account issues, feedback, or a question about the site \u2014 raise a ticket here.": "नागरी तक्रारीव्यतिरिक्त इतर कोणत्याही गोष्टीसाठी \u2014 खाते समस्या, अभिप्राय किंवा संकेतस्थळाबाबत प्रश्न \u2014 येथे तिकीट नोंदवा.",
    "Forms, circulars, notifications and guidelines you can download.": "डाउनलोड करता येणारे अर्ज, परिपत्रके, अधिसूचना आणि मार्गदर्शक तत्त्वे.",
    "Frequently Asked Questions": "वारंवार विचारले जाणारे प्रश्न",
    "Funds": "निधी",
    "Government Funds": "शासकीय निधी",
    "Government Projects": "शासकीय प्रकल्प",
    "In progress": "प्रगतीपथावर",
    "LOKSETU connects the citizens of Maharashtra with their government.": "LOKSETU महाराष्ट्रातील नागरिकांना त्यांच्या शासनाशी जोडते.",
    "Last 30 days": "गेले ३० दिवस",
    "Last updated": "शेवटचे अद्ययावत",
    "Latest announcements": "ताज्या घोषणा",
    "Latest schemes": "ताज्या योजना",
    "Log in": "लॉग इन करा",
    "Log out": "लॉग आउट करा",
    "Map": "नकाशा",
    "My dashboard": "माझा डॅशबोर्ड",
    "My support tickets": "माझी सहाय्य तिकिटे",
    "New ticket": "नवीन तिकीट",
    "News": "बातम्या",
    "No announcements yet.": "अद्याप कोणतीही घोषणा नाही.",
    "No complaints filed yet.": "अद्याप कोणतीही तक्रार दाखल नाही.",
    "No documents listed yet.": "अद्याप कोणतेही दस्तऐवज नाहीत.",
    "No funds listed yet.": "अद्याप कोणताही निधी नमूद नाही.",
    "No notifications yet.": "अद्याप कोणतीही सूचना नाही.",
    "No projects listed yet.": "अद्याप कोणताही प्रकल्प नमूद नाही.",
    "No questions added yet.": "अद्याप कोणतेही प्रश्न जोडलेले नाहीत.",
    "No reports listed yet.": "अद्याप कोणताही अहवाल नाही.",
    "No schemes yet.": "अद्याप कोणतीही योजना नाही.",
    "No tickets yet.": "अद्याप कोणतेही तिकीट नाही.",
    "Notifications": "सूचना",
    "Official Documents": "अधिकृत कागदपत्रे",
    "Official source": "अधिकृत स्रोत",
    "Open report": "अहवाल उघडा",
    "Pending": "प्रलंबित",
    "Privacy": "गोपनीयता",
    "Projects": "प्रकल्प",
    "Recent complaints": "अलीकडील तक्रारी",
    "Report it. Track it. See it fixed.": "तक्रार नोंदवा. मागोवा घ्या. निराकरण पहा.",
    "Reports & Publications": "अहवाल व प्रकाशने",
    "Reports": "अहवाल",
    "Resolution rate": "निराकरण दर",
    "Resolved": "निराकरण झाले",
    "Resources": "संसाधने",
    "Response": "प्रतिसाद",
    "Schemes": "योजना",
    "Showing complaints in your scope only.": "फक्त तुमच्या कार्यक्षेत्रातील तक्रारी दर्शवल्या आहेत.",
    "Site content": "संकेतस्थळावरील सामग्री",
    "Start date": "प्रारंभ तारीख",
    "Status breakdown": "स्थितीनुसार विभागणी",
    "Status stages": "स्थिती टप्पे",
    "Submit ticket": "तिकीट सादर करा",
    "Submitted": "सादर केले",
    "Support tickets": "सहाय्य तिकिटे",
    "Support": "सहाय्य",
    "Terms": "अटी",
    "Top categories": "आघाडीचे प्रवर्ग",
    "Top departments": "आघाडीचे विभाग",
    "Top districts": "आघाडीचे जिल्हे",
    "Total complaints": "एकूण तक्रारी",
    "Total": "एकूण",
    "Track a complaint": "तक्रारीचा मागोवा घ्या",
    "Utilized": "वापरलेला निधी",
    "View all tickets": "सर्व तिकिटे पहा",
    "Your recent tickets": "तुमची अलीकडील तिकिटे",
}

HEADER = (
    "Project-Id-Version: LOKSETU\n"
    "Report-Msgid-Bugs-To: \n"
    "MIME-Version: 1.0\n"
    "Content-Type: text/plain; charset=UTF-8\n"
    "Content-Transfer-Encoding: 8bit\n"
    "Language: mr\n"
)


def po_escape(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def write_po(path):
    parts = [
        '# Marathi translation for LOKSETU.',
        '# AI-assisted machine translation of the site chrome (nav, buttons, headings).',
        '# Please have a native Marathi speaker review before relying on it for real users.',
        'msgid ""',
        'msgstr ""',
    ]
    for line in HEADER.splitlines(keepends=True):
        parts.append(f'"{po_escape(line)}"')
    parts.append('')
    for msgid, msgstr in TRANSLATIONS.items():
        parts.append(f'msgid "{po_escape(msgid)}"')
        parts.append(f'msgstr "{po_escape(msgstr)}"')
        parts.append('')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(parts))


def compile_mo(path_mo):
    """Write a standard GNU MO file directly from TRANSLATIONS + HEADER (no .po parsing)."""
    messages = {'': HEADER}
    messages.update(TRANSLATIONS)

    keys = sorted(messages.keys())
    ids = b''
    strs = b''
    key_offsets = []
    value_offsets = []
    for key in keys:
        key_b = key.encode('utf-8')
        value_b = messages[key].encode('utf-8')
        key_offsets.append((len(key_b), len(ids)))
        value_offsets.append((len(value_b), len(strs)))
        ids += key_b + b'\x00'
        strs += value_b + b'\x00'

    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart + len(ids)
    koffsets = [(length, offset + keystart) for length, offset in key_offsets]
    voffsets = [(length, offset + valuestart) for length, offset in value_offsets]

    output = struct.pack('Iiiiiii', 0x950412de, 0, len(keys), 7 * 4, 7 * 4 + len(keys) * 8,
                         0, 7 * 4 + 2 * len(keys) * 8)
    for length, offset in koffsets:
        output += struct.pack('ii', length, offset)
    for length, offset in voffsets:
        output += struct.pack('ii', length, offset)
    output += ids
    output += strs
    with open(path_mo, 'wb') as f:
        f.write(output)


if __name__ == '__main__':
    import sys
    po_path, mo_path = sys.argv[1], sys.argv[2]
    write_po(po_path)
    compile_mo(mo_path)
    print('wrote', po_path, mo_path)
