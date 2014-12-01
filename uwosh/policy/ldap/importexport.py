
from Products.CMFCore.utils import getToolByName
from Products.LDAPMultiPlugins import manage_addLDAPMultiPlugin

def install(context):
    if not context.readDataFile('uwosh.policy.ldap.txt'):
        return 
    setupLDAPPlugin(context)

def setupLDAPPlugin(context):
    ldap_plugin_id = 'ldap_authentication_netid'
    SUBTREE = 2 # this value comes from the zmi "Add LDAP Multi Plugin" html source

    acl_users = context.getSite().acl_users
    if hasattr(acl_users, ldap_plugin_id):
        logger = context.getLogger('uwosh.policy.ldap')
        logger.warning('Not configuring LDAP plugin, because "acl_users.%s" already exists.' % ldap_plugin_id)
        return
    
    manage_addLDAPMultiPlugin(
        acl_users,
        id=ldap_plugin_id,
        title='LDAP Authentication NetID',
        LDAP_server='uwoad4.uwoad.it.uwosh.edu:636',
        login_attr='sAMAccountName',
        uid_attr='sAMAccountName',
        users_base='ou=campus,dc=uwoad,dc=it,dc=uwosh,dc=edu', 
        users_scope=SUBTREE, 
        roles='Anonymous', 
        groups_base='ou=security groups,ou=campus,dc=uwoad,dc=it,dc=uwosh,dc=edu', 
        groups_scope=SUBTREE, 
        binduid='', # cn=ploneauth,ou=administrative,ou=job accounts,ou=campus,dc=uwoad,dc=it,dc=uwosh,dc=edu
        bindpwd='', 
#        extra_user_filter='(!(objectclass=computer))',
        binduid_usage=1, 
        rdn_attr='sAMAccountName', 
        local_groups=False, 
        use_ssl=True,
        encryption='SHA', 
        read_only=True
    )
                         
    ldap_auth = getattr(acl_users, ldap_plugin_id)          
    
    ldap_schema = {
        'mail': { 
            'public_name': 'email', 
            'binary': False, 
            'ldap_name': 'mail', 
            'friendly_name': 'Email Address', 
            'multivalued': False
        }, 
        'sn': { 
            'public_name': 'lastname', 
            'binary': False, 
            'ldap_name': 'sn', 
            'friendly_name': 'Last Name', 
            'multivalued': False
        },
        'givenName': {
            'public_name': 'firstname',
            'binary': False,
            'ldap_name': 'givenName',
            'friendly_name': 'First Name',
            'multivalued': False
        },
        'uid': { 
            'public_name': '', 
            'binary': False, 
            'ldap_name': 'uid', 
            'friendly_name': 'uid', 
            'multivalued': False
        },
        'eduPersonAffiliation': { 
            'public_name': 'eduPersonAffiliation', 
            'binary': False, 
            'ldap_name': 'eduPersonAffiliation', 
            'friendly_name': 'eduPersonAffiliation', 
            'multivalued': True
        },
        'eduPersonPrimaryAffiliation': { 
            'public_name': 'eduPersonPrimaryAffiliation', 
            'binary': False, 
            'ldap_name': 'eduPersonPrimaryAffiliation', 
            'friendly_name': 'eduPersonPrimaryAffiliation', 
            'multivalued': False
        },
        'ou': {
            'public_name': 'ou',
            'binary': False,
            'ldap_name': 'ou',
            'friendly_name': 'Organizational Unit',
            'multivalued': False
        },
        'uwodepartmentassoc': {
            'public_name': 'uwodepartmentassoc',
            'binary': False,
            'ldap_name': 'uwodepartmentassoc',
            'friendly_name': 'UWO Department Association',
            'multivalued': False
        },
        'l': {
            'public_name': 'location',
            'binary': False,
            'ldap_name': 'l',
            'friendly_name': 'Location',
            'multivalued': False
        },
        'telephoneNumber': {
            'public_name': 'phone',
            'binary': False,
            'ldap_name': 'telephoneNumber',
            'friendly_name': 'Phone Number',
            'multivalued': False
        },
        'mailUserStatus': {
            'public_name': 'mailUserStatus',
            'binary': False,
            'ldap_name': 'mailUserStatus',
            'friendly_name': 'Mail User Status',
            'multivalued': False
        },
        'uwomailstop': {
            'public_name': 'uwomailstop',
            'binary': False,
            'ldap_name': 'uwomailstop',
            'friendly_name': 'UWO Mail Stop',
            'multivalued': False
        },
        'displayName': {
            'public_name': 'displayname',
            'binary': False,
            'ldap_name': 'displayName',
            'friendly_name': 'Display Name',
            'multivalued': False
        },
        'displayname': {
            'public_name': 'fullname',
            'binary': False,
            'ldap_name': 'displayname',
            'friendly_name': 'Display Name',
            'multivalued': False
        },
        'department': {
            'public_name': '', 
            'binary': False,
            'ldap_name': 'department',
            'friendly_name': 'department',
            'multivalued': False
        },
        'physicalDeliveryOfficeName': {
            'public_name': '', 
            'binary': False,
            'ldap_name': 'physicalDeliveryOfficeName',
            'friendly_name': 'physicalDeliveryOfficeName',
            'multivalued': False
        },
        'sAMAccountName': {
            'public_name': '', 
            'binary': False,
            'ldap_name': 'sAMAccountName',
            'friendly_name': 'sAMAccountName',
            'multivalued': False
        },
        
    }
    
    ldap_auth.acl_users.setSchemaConfig(ldap_schema)
    ldap_auth.acl_users._user_objclasses = ['user']
    ldap_auth.manage_activateInterfaces(['IUserEnumerationPlugin', 'IPropertiesPlugin', 'IAuthenticationPlugin'])
    movePluginToHeadOfList(acl_users.plugins, 'IPropertiesPlugin', ldap_plugin_id)

    # fix timeout
    ldap_auth.acl_users.manage_addServer(
        'uwoad4.uwoad.it.uwosh.edu'
      , port=636
      , use_ssl=True
      , conn_timeout=5
      , op_timeout=10
      )
    # set another server
    ldap_auth.acl_users.manage_addServer(
        'uwoad5.uwoad.it.uwosh.edu'
      , port=636
      , use_ssl=True
      , conn_timeout=5
      , op_timeout=10
      )

    
def movePluginToHeadOfList(plugin_registry, plugin_type, plugin_id):
    interface = plugin_registry._getInterfaceFromName(plugin_type)
    index = plugin_registry._getPlugins(interface).index(plugin_id)
    while index > 0:
        plugin_registry.movePluginsUp(interface, [plugin_id])
        new_index = plugin_registry._getPlugins(interface).index(plugin_id)
        if new_index >= index: 
             # The plugin didn't move up. We calmly sidestep the infinite loop.
            break
        index = new_index
            
