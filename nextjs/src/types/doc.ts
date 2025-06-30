import { FileType, FormatUserType } from './common';

export type DocRecordType = {
    _id: string;
    brainId: string;
    doc: FileType;
    fileId: string;
    embedding_api_key: string;
    userId: FormatUserType;
    favoriteByUsers: string[];
};
