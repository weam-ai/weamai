import * as yup from 'yup';

export const addThreadKeys = yup.object({
    content: yup.string().required('enter content'),
})