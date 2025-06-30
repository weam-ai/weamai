const COLLECTION_REF_UPDATE = {
    USER: {
        company: { arrayType: ['users'] },
        brains: {
            objectType: ['user'],
        },
        chat: { objectType: ['user'] },
        chatmember: { objectType: ['user'] },
        chatdocs: { arrayType: ['docShare'] },
        notificationList: { objectType: ['user', 'sender'] },
        thread: { arrayType: ['reaction'], objectType: ['user'] },
        workspaceuser: { objectType: ['user'] },
        shareBrain: { objectType: ['user'] },
        customgpt: { objectType: ['owner'] }, 
        prompts: { objectType: ['user'] },
        teamUser: { arrayType: ['teamUsers'] },
    },
    BRAINS: {
        thread: { objectType: ['brain'] },
        shareBrain: { objectType: ['brain'] },
        chat: { objectType: ['brain'] },
        chatmember: { objectType: ['brain'] },
        prompts: { objectType: ['brain'] },
        customgpt: { objectType: ['brain'] },
    },
    FILE: {
        brains: { arrayType: ['doc'] },
        user: { objectType: ['profile'] }
    },
    TEAMUSER:{
        workspace:{arrayType:['teams']},
        brains:{arrayType:['teams']}
    }
}

const SELECTED_IGNORE_KEYS = [
    '_id',
    'id',
    '__v',
    'createdAt',
    'updatedAt',
    'createdBy',
    'updatedBy',
    'fcmTokens',
    'roleId',
    'roleCode',
    'promptLimit',
    'invited',
]

module.exports = {
    COLLECTION_REF_UPDATE,
    SELECTED_IGNORE_KEYS
}