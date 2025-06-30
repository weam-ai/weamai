import * as yup from 'yup';



export const promptCreateSchema = yup.object({
    name: yup.string().required('Prompt Name is required'),
    content: yup.string().required('Prompt Content is required'),
    brain: yup
        .array()
        .of(
            yup.object().shape({
                value: yup.string().required('Please select a brain'),
                label: yup.string().optional(), // optional, validate label if needed
            })
        )
        .min(1, 'Please select at least one brain'),
    addinfo: yup.object().nullable().optional()
})
