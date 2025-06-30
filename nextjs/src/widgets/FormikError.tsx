const FormikError = ({ errors, field, index }:any) => {
    if (!errors || !errors[field]) return null;

    return (
        <>
            {index >= 0 ? <>
                {
                    typeof errors[field] == 'object' && errors[field][index] != null ? <p className="text-xs font-medium mt-1 text-red text-font-14">{errors[field][index]}</p> :''
                }
            </>
                : <>
                    <p className="text-xs font-medium mt-1 text-red text-font-14">
                        {errors[field]}
                    </p>
                </>}
        </>
    );
};

export default FormikError;

