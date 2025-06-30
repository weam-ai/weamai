const getNestedError = (errors, path) => {
    return path.split('.').reduce((acc, part) => acc && acc[part], errors);
};

const ValidationError = ({ errors, field }) => {
    const errorMessage = getNestedError(errors, field);
    if (!errorMessage) return null;

    return (
        <p className="text-font-13 font-medium mt-1 text-red">
            {errorMessage?.message}
        </p>
    );
};

export default ValidationError;

