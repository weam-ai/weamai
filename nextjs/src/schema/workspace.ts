import * as yup from 'yup';

export const addWorkSpaceKeys = yup.object({
    title: yup.string().required('enter the workspace name'),
    // members: yup.array().of(
    //     yup.object().shape({
    //         email: yup.string().email().required(),
    //         id: yup.string().required(),
    //     })
    // ).min(1, 'Please select at least one member'),
    // role: yup.string().required(), 
}) 

export const addMemberWorkSpaceKeys = yup.object({
    members: yup.array().of(
        yup.object().shape({
            email: yup.string().email().required(),
            id: yup.string().required(),
        })
    ).min(1, 'Please select at least one member'),
    // role: yup.string().required(), 
}) 