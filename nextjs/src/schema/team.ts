import * as yup from 'yup';

export const teamSchema = yup.object({
    teamName: yup.string().required('Enter the team name'),
    members: yup
        .array()
        .transform((value, originalValue) =>
            typeof originalValue === 'string' && originalValue === ''
                ? []
                : value
        )
        .min(2, 'Select at least 2 members for a team')
        .required('Select member to add in team')
        .default([]),

        teamsInput:yup
        .array()
        .transform((value, originalValue) =>
            typeof originalValue === 'string' && originalValue === ''
                ? []
                : value
        )
        // .min(1, 'Please Select A Team')
        // .required('Select a team')
        .default([]) 
        .optional(),
    
});

export const workspaceTeamSchema=yup.object({
    teamsInput:yup
  .array()
  .transform((value, originalValue) =>
      typeof originalValue === 'string' && originalValue === ''
          ? []
          : value
  )
  .min(1, 'Please Select A Team')
  .required('Select a team')
  .default([]),
})
