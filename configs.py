# Server Configs
ADEPT = 362987473154080778
LOGS_CHANNEL = f"547896873776578563/{ADEPT}"
WELCOME_CHANNEL = f"470775922069471252/{ADEPT}"
SETUP_CHANNEL = "943322082001956864"

TICKET_CATEGORY = 899725071504015421
TICKET_ARCHIVE_CATEGORY = 903831890866372658

# Roles
PROG_ROLE = 363042185295167490
NETWORK_ROLE = 363042228035125266
DECBAC_ROLE = 775759126578855957
TEACHER_ROLE = 775751726480883783
REGULARS_ROLE = 376941530461503489

TRUST_ROLE = 434423894238298112
ADMIN_ROLE = 363015309562478593

MUTED_ROLE = 363031112664219648
MORON_ROLE = 559825539993698316

# Messages
# TODO: Use/Make a translation service?
WELCOME_TITLE = "Bonjour et bienvenue à l'ADEPT!"
WELCOME_MESSAGE = "Pour commencer, nous allons devoir vous posez quelques questions afin de mieux vous connaitre.\n\n**{content}**"
WELCOME_FOOTER = "* Le masculin est uniquement utilisé afin d'alléger les questions."
WELCOME_SERVER = """
Bienvenue {name} sur le serveur de l'ADEPT Informatique,

veuillez suivre les étapes en message privé pour avoir accès au serveur!

Assurez-vous également de regardez les réglements dans <#471133862442041355> après avoir complété les étapes
"""

TICKET_VIEW_MESSAGE = "Bonjour! Tu peux ouvrir un ticket en utilisant les boutons ci-dessous:"
TICKET_MESSAGE = """
[{ticket_type}]
Salut {plaintive}, 

Nous voulons vous informez que le respect de votre confidentialité est notre priorité.
Votre identité ne sera **JAMAIS** dévoilée à qui que ce soit sans votre consentement.
Les seuls connaisant votre identité sont les membres du CA de l'ADEPT-Informatique (Admins).

Vous pouvez utiliser `{prefix}close` pour fermer ce ticket.

Sincèrement,
{admins}
"""

# Custom IDs
TICKET_COMPLAINT_ID = "ticket_view_1.0:Complaint"
TICKET_MORON_ID = "ticket_view_1.0:Moron"
TICKET_CLOSE_ID = "ticket_view_1.0:Close"

# Emojis
CHECK_REACT = u"\u2705"
CROSS_REACT = u"\u274C"

ENVIRONMENT = {
    **dotenv_values(".env"),
    **os.environ
}