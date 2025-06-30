import * as yup from 'yup';

export const addMemberChatKeys = yup.object({
    members: yup.array().of(
        yup.object().shape({
            email: yup.string().email().required(),
            id: yup.string().required(),
        })
    ).min(1, 'Please select at least one member')
}) 