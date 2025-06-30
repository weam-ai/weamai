import { NOT_FORBIDDEN_FILE_EXTENSIONS } from './constant';

/**
 * Utility function to check if a file has a forbidden extension
 * @param fileName - The name of the file to check
 * @returns boolean - true if file has forbidden extension, false otherwise
 */
export const hasExtraExtension = (fileName: string): boolean => {
    const fileExtension = fileName.split('.').pop()?.toLowerCase();
    if (!fileExtension) return false;
    
    return NOT_FORBIDDEN_FILE_EXTENSIONS.some(notForbiddenExt => 
        fileExtension === notForbiddenExt || fileExtension === notForbiddenExt.toLowerCase()
    );
};

/**
 * Get file extension from filename
 * @param fileName - The name of the file
 * @returns string | undefined - The file extension or undefined if no extension
 */
export const getFileExtension = (fileName: string): string | undefined => {
    return fileName.split('.').pop()?.toLowerCase();
};

/**
 * Check if file extension is in a list of allowed extensions
 * @param fileName - The name of the file
 * @param allowedExtensions - Array of allowed extensions
 * @returns boolean - true if extension is allowed
 */
export const isExtensionAllowed = (fileName: string, allowedExtensions: string[]): boolean => {
    const extension = getFileExtension(fileName);
    if (!extension) return false;
    
    return allowedExtensions.some(allowedExt => 
        extension === allowedExt.toLowerCase()
    );
};

/**
 * Validate file against forbidden extensions
 * @param fileName - The name of the file to validate
 * @returns { isValid: boolean, errorMessage?: string }
 */
export const validateFileExtension = (fileName: string): { isValid: boolean; errorMessage?: string } => {
    if (!hasExtraExtension(fileName)) {
        return {
            isValid: false,
            errorMessage: `File type not supported: ${getFileExtension(fileName)}`
        };
    }
    
    return { isValid: true };
}; 