import { useState, useCallback } from 'react';
import commonApi from '../../api';
import { MODULE_ACTIONS } from '@/utils/constant';

interface UsePageOperationsProps {
  onPageCreated?: (pageData: any, isUpdate?: boolean) => void;
  onError?: (error: string) => void;
}

export const usePageOperations = ({ 
  onPageCreated, 
  onError 
}: UsePageOperationsProps = {}) => {
  const [isCreatingPage, setIsCreatingPage] = useState(false);

  const createPageFromResponse = async (pageData: {
    originalMessageId: string;
    title: string;
    content: string;
    chatId: string;
    user: any;
    brain: any;
    model: any;
    tokens?: any;
    responseModel?: string;
    responseAPI?: string;
    companyId: string;
  }) => {
    try {
      setIsCreatingPage(true);
      
      console.log('usePageOperations - Sending pageData:', JSON.stringify(pageData, null, 2));
      
      const response = await commonApi({
        action: MODULE_ACTIONS.PAGE_CREATE,
        data: pageData,
        errorToast: true
      });

      console.log('usePageOperations - Success result:', response);
      
      if (onPageCreated && response?.data) {
        onPageCreated(response.data, response.data.isUpdate);
      }
      
      return response;
    } catch (error) {
      console.error('Error creating page:', error);
      if (onError) {
        onError(error.message);
      }
      throw error;
    } finally {
      setIsCreatingPage(false);
    }
  };

  const getAllPages = async (query = {}, options = {}) => {
    try {
      console.log('usePageOperations - getAllPages called with:', { query, options });
      
      const response = await commonApi({
        action: MODULE_ACTIONS.PAGE_LIST,
        data: { query, options },
        errorToast: true
      });

      console.log('usePageOperations - Success result:', response);
      return response;
    } catch (error) {
      console.error('Error getting pages:', error);
      throw error;
    }
  };

  const getPageById = async (pageId: string) => {
    try {
      const response = await commonApi({
        action: MODULE_ACTIONS.PAGE_VIEW,
        parameters: [pageId],
        errorToast: true
      });

      return response;
    } catch (error) {
      console.error('Error getting page:', error);
      throw error;
    }
  };

  const updatePage = async (pageId: string, updateData: any) => {
    try {
      console.log('usePageOperations - updatePage called with:', { pageId, updateData });
      
      const response = await commonApi({
        action: MODULE_ACTIONS.PAGE_UPDATE,
        parameters: [pageId],
        data: updateData,
        errorToast: true
      });

      console.log('usePageOperations - updatePage success result:', response);
      return response;
    } catch (error) {
      console.error('Error updating page:', error);
      throw error;
    }
  };

  const deletePage = async (pageId: string) => {
    try {
      const response = await commonApi({
        action: MODULE_ACTIONS.PAGE_DELETE,
        parameters: [pageId],
        errorToast: true
      });

      return response;
    } catch (error) {
      console.error('Error deleting page:', error);
      throw error;
    }
  };

  return {
    createPageFromResponse,
    getAllPages,
    getPageById,
    updatePage,
    deletePage,
    isCreatingPage,
  };
};
