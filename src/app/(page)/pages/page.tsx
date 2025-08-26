'use client';
import React, { useState, useEffect, useMemo } from 'react';
import { useSearchParams } from 'next/navigation';
import { getCurrentUser, getCompanyId } from '@/utils/handleAuth';
import { decodedObjectId, encodedObjectId } from '@/utils/helper';
import { usePageOperations } from '@/hooks/chat/usePageOperations';
import routes from '@/utils/routes';
import DocumentIcon from '@/icons/DocumentIcon';
import SearchIcon from '@/icons/Search';
// Using simple SVG icons instead of importing components
import { format } from 'date-fns';
import Toast from '@/utils/toast';
import  { useRouter } from 'next/navigation';

interface Page {
    _id: string;
    title: string;
    content: string;
    originalMessageId: string;
    chatId: string;
    user: any;
    brain: any;
    model: any;
    tokens?: any;
    responseModel?: string;
    responseAPI?: string;
    companyId: string;
    createdAt: string;
    updatedAt: string;
}

const PagesPage = () => {
    const searchParams = useSearchParams();
    const router = useRouter();
    const currentUser = useMemo(() => getCurrentUser(), []);
    const companyId = useMemo(() => getCompanyId(currentUser), [currentUser]);
    const brainId = searchParams.get('b') ? decodedObjectId(searchParams.get('b')!) : null;
    
    const [pages, setPages] = useState<Page[]>([]);
    const [loading, setLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [filteredPages, setFilteredPages] = useState<Page[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);
    const [loadingMore, setLoadingMore] = useState(false);
    
    // Edit and Delete states
    const [editingPage, setEditingPage] = useState<Page | null>(null);
    const [editTitle, setEditTitle] = useState('');
    const [isEditing, setIsEditing] = useState(false);
    const [deletingPage, setDeletingPage] = useState<string | null>(null);

    const { getAllPages, updatePage, deletePage } = usePageOperations({
        onError: (error) => {
            console.error('Error loading pages:', error);
            setError(error);
        }
    });

    useEffect(() => {
        const loadPages = async () => {
            if (!companyId) return;
            
            try {
                setLoading(true);
                setError(null);
                setCurrentPage(1);
                setHasMore(true);
                console.log('Loading pages for companyId:', companyId, 'brainId:', brainId);
                
                const result = await getAllPages({
                    query: {
                        companyId: companyId
                        // Removed brain filter since brain objects don't have _id field
                    },
                    options: {
                        page: 1,
                        limit: 10,
                        sort: { createdAt: -1 } // Descending order by creation date
                    }
                });
                
                console.log('Pages API response:', result);
                
                if (result?.data) {
                    const pagesData = Array.isArray(result.data) ? result.data : [];
                    console.log('Setting pages:', pagesData.length, 'pages');
                    
                    // Ensure pages are sorted in descending order by createdAt
                    const sortedPages = pagesData.sort((a, b) => 
                        new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
                    );
                    
                    setPages(sortedPages);
                    // Check if there are more pages based on total count
                    const totalPages = Math.ceil((result.paginator?.itemCount || 0) / 10);
                    setHasMore(totalPages > 1);
                } else {
                    console.log('No data in response');
                    setPages([]);
                    setHasMore(false);
                }
            } catch (error) {
                console.error('Error loading pages:', error);
                setError(error instanceof Error ? error.message : 'Failed to load pages');
                setPages([]);
                setHasMore(false);
            } finally {
                setLoading(false);
            }
        };

        loadPages();
    }, [companyId, brainId]);

    useEffect(() => {
        const filtered = pages.filter(page =>
            page.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            page.content.toLowerCase().includes(searchTerm.toLowerCase())
        );
        setFilteredPages(filtered);
    }, [pages, searchTerm]);

    const handlePageClick = (page: Page) => {
        // Navigate to the original chat where this page was created
        const chatUrl = `${routes.chat}/${page.chatId}?b=${encodedObjectId(page.brain?._id || '')}`;
        router.push(chatUrl);
    };

    const formatDate = (dateString: string) => {
        try {
            return format(new Date(dateString), 'MMM dd, yyyy');
        } catch {
            return 'Unknown date';
        }
    };

    const truncateContent = (content: string, maxLength: number = 150) => {
        if (content.length <= maxLength) return content;
        return content.substring(0, maxLength) + '...';
    };

    const loadMore = async () => {
        if (!companyId || loadingMore || !hasMore) return;
        
        try {
            setLoadingMore(true);
            const nextPage = currentPage + 1;
            
            console.log('Loading more pages, page:', nextPage);
            
            const result = await getAllPages({
                query: {
                    companyId: companyId
                },
                options: {
                    page: nextPage,
                    limit: 10,
                    sort: { createdAt: -1 }
                }
            });
            
            if (result?.data) {
                const newPages = Array.isArray(result.data) ? result.data : [];
                console.log('Received new pages:', newPages.length);
                
                // Check for duplicates and only add new pages
                const existingIds = new Set(pages.map(page => page._id));
                const uniqueNewPages = newPages.filter(page => !existingIds.has(page._id));
                
                console.log('Unique new pages:', uniqueNewPages.length);
                
                if (uniqueNewPages.length > 0) {
                    // Add new pages and maintain descending order by createdAt
                    setPages(prev => {
                        const combined = [...prev, ...uniqueNewPages];
                        return combined.sort((a, b) => 
                            new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
                        );
                    });
                    setCurrentPage(nextPage);
                    
                    // Check if there are more pages based on total count
                    const totalPages = Math.ceil((result.paginator?.itemCount || 0) / 10);
                    setHasMore(nextPage < totalPages);
                } else {
                    // No new pages, stop loading more
                    setHasMore(false);
                }
            } else {
                setHasMore(false);
            }
        } catch (error) {
            console.error('Error loading more pages:', error);
        } finally {
            setLoadingMore(false);
        }
    };

    // Handle page edit
    const handleEditPage = (page: Page) => {
        console.log('handleEditPage called with:', page);
        console.log('Setting editingPage to:', page);
        console.log('Setting editTitle to:', page.title);
        setEditingPage(page);
        setEditTitle(page.title);
        setIsEditing(false); // Should be false initially
        console.log('State should now be set');
    };

    // Handle page update
    const handleUpdatePage = async () => {
        if (!editingPage || !editTitle.trim() || isEditing) return;
        
        try {
            setIsEditing(true);
            console.log('Updating page:', editingPage._id, 'with title:', editTitle.trim());
            
            await updatePage(editingPage._id, { title: editTitle.trim() });
            
            // Update local state
            setPages(prev => prev.map(p => 
                p._id === editingPage._id 
                    ? { ...p, title: editTitle.trim(), updatedAt: new Date().toISOString() }
                    : p
            ));
            
            // Close modal and reset state
            setEditingPage(null);
            setEditTitle('');
            setIsEditing(false);
            
            console.log('Page updated successfully');
            Toast('Page updated successfully!', 'success');
        } catch (error) {
            console.error('Error updating page:', error);
            setIsEditing(false);
            // Show error to user
            Toast('Failed to update page. Please try again.', 'error');
        }
    };

    // Handle page delete
    const handleDeletePage = async (pageId: string) => {
        setDeletingPage(pageId);
    };
    
    // Confirm and execute delete
    const confirmDeletePage = async (pageId: string) => {
        try {
            await deletePage(pageId);
            
            // Remove from local state
            setPages(prev => prev.filter(p => p._id !== pageId));
            
            setDeletingPage(null);
            Toast('Page deleted successfully!', 'success');
        } catch (error) {
            console.error('Error deleting page:', error);
            setDeletingPage(null);
            Toast('Failed to delete page. Please try again.', 'error');
        }
    };

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <header className="h-[68px] min-h-[68px] flex items-center space-x-2 py-2 md:pl-[15px] md:pr-[15px] pl-[50px] pr-[15px] max-md:sticky max-md:top-0 z-10 bg-white border-b border-gray-200">
                <div className="size-[30px] flex items-center justify-center rounded-full p-1">
                    <DocumentIcon width={20} height={20} className="fill-b2 object-contain" />
                </div>
                <p className="text-font-16 font-bold">
                    Pages
                </p>
                <div className="ml-auto text-sm text-gray-500">
                    {filteredPages.length} page{filteredPages.length !== 1 ? 's' : ''}
                </div>
            </header>

            {/* Search Bar */}
            <div className="p-4 border-b border-gray-200">
                <div className="relative">
                    <SearchIcon width={20} height={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 fill-gray-400" />
                    <input
                        type="text"
                        placeholder="Search pages..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4">
                {error && (
                    <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
                        <p className="text-red-800 text-sm">Error: {error}</p>
                    </div>
                )}
                
                {loading ? (
                    <div className="flex items-center justify-center h-64">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    </div>
                ) : filteredPages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-64 text-gray-500">
                        <DocumentIcon width={48} height={48} className="fill-gray-300 mb-4" />
                        <p className="text-lg font-medium mb-2">
                            {searchTerm ? 'No pages found' : 'No pages yet'}
                        </p>
                        <p className="text-sm text-gray-400">
                            {searchTerm 
                                ? 'Try adjusting your search terms' 
                                : 'Pages created from chat responses will appear here'
                            }
                        </p>
                    </div>
                ) : (
                    <div className="space-y-3">
                        <div className="grid gap-3">
                            {filteredPages.map((page) => (
                                <div
                                    key={page._id}
                                    className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md hover:border-gray-300 transition-all duration-200 group relative"
                                >
                                    {/* Page Content - Clickable for viewing */}
                                    <div 
                                        onClick={() => handlePageClick(page)}
                                        className="cursor-pointer"
                                    >
                                        {/* Compact Header with title, model, and date */}
                                        <div className="flex items-center justify-between">
                                            <div className="flex-1 min-w-0">
                                                <h3 className="text-base font-semibold text-gray-900 group-hover:text-blue-600 transition-colors truncate">
                                                    {page.title}
                                                </h3>
                                                <p className="text-xs text-gray-500 mt-1">
                                                    {formatDate(page.createdAt)}
                                                </p>
                                            </div>
                                            
                                            {/* Right side: Model + Action Icons */}
                                            <div className="flex items-center space-x-3 ml-3">
                                                {/* Model Label */}
                                                {page.responseModel && (
                                                    <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap">
                                                        {page.responseModel}
                                                    </span>
                                                )}
                                                
                                                {/* Action Icons - Always visible, subtle on hover */}
                                                <div className="flex items-center space-x-1 opacity-60 group-hover:opacity-100 transition-opacity duration-200">
                                                    {/* Edit Icon */}
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            handleEditPage(page);
                                                        }}
                                                        className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors duration-200 relative group/icon"
                                                        title="Edit page"
                                                    >
                                                        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" className="fill-current">
                                                            <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                                                        </svg>
                                                        {/* Hover Tooltip */}
                                                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs text-white bg-gray-800 rounded opacity-0 group-hover/icon:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-10">
                                                            Edit page
                                                            <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-800"></div>
                                                        </div>
                                                    </button>
                                                    
                                                    {/* Delete Icon */}
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            handleDeletePage(page._id);
                                                        }}
                                                        disabled={deletingPage === page._id}
                                                        className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors duration-200 disabled:opacity-50 relative group/icon"
                                                        title="Delete page"
                                                    >
                                                        {deletingPage === page._id ? (
                                                            <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-red-600"></div>
                                                        ) : (
                                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" className="fill-current">
                                                                <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                                                            </svg>
                                                        )}
                                                        {/* Hover Tooltip */}
                                                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs text-white bg-gray-800 rounded opacity-0 group-hover/icon:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-10">
                                                            Delete page
                                                            <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-800"></div>
                                                        </div>
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                        
                        {/* Load More Button */}
                        {hasMore && !searchTerm && pages.length >= 10 && (
                            <div className="flex justify-center pt-4">
                                <button
                                    onClick={loadMore}
                                    disabled={loadingMore}
                                    className="px-6 py-3 text-sm font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                                >
                                    {loadingMore ? (
                                        <div className="flex items-center space-x-2">
                                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                                            <span>Loading...</span>
                                        </div>
                                    ) : (
                                        'Load More Pages'
                                    )}
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Edit Page Modal */}
            {editingPage && (
                <div 
                    className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
                    onClick={() => {
                        setEditingPage(null);
                        setEditTitle('');
                        setIsEditing(false);
                    }}
                >
                    <div 
                        className="bg-white rounded-xl p-6 w-full max-w-md mx-4 shadow-2xl border border-gray-200"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="mb-4">
                            <label htmlFor="edit-page-title" className="block text-sm font-medium text-gray-700 mb-1">
                                Page Title
                            </label>
                            <input
                                id="edit-page-title"
                                type="text"
                                value={editTitle}
                                onChange={(e) => setEditTitle(e.target.value)}
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter' && editTitle.trim()) {
                                        handleUpdatePage();
                                    }
                                }}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                placeholder="Enter page title..."
                                autoFocus
                            />
                        </div>
                        
                        {/* Buttons Container */}
                        <div className="flex justify-end space-x-3">
                            {/* Save Button */}
                            <button
                                onClick={handleUpdatePage}
                                disabled={isEditing || !editTitle.trim()}
                                className="px-6 py-3 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50"
                            >
                                Save
                            </button>
                            
                            {/* Cancel Button */}
                            <button
                                onClick={() => {
                                    setEditingPage(null);
                                    setEditTitle('');
                                    setIsEditing(false);
                                }}
                                disabled={isEditing}
                                className="px-6 py-3 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Delete Confirmation Modal */}
            {deletingPage && (
                <div 
                    className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
                    onClick={() => setDeletingPage(null)}
                >
                    <div 
                        className="bg-white rounded-xl p-6 w-full max-w-md mx-4 shadow-2xl border border-gray-200"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="mb-4">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">Delete Page</h3>
                            <p className="text-sm text-gray-600">
                                Are you sure you want to delete this page? This action cannot be undone.
                            </p>
                        </div>
                        
                        {/* Buttons Container - Same style as Edit Modal */}
                        <div className="flex justify-end space-x-3">
                            {/* Confirm Button - First (left side) */}
                            <button
                                onClick={() => confirmDeletePage(deletingPage)}
                                className="px-6 py-3 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                            >
                                Confirm Delete
                            </button>
                            
                            {/* Cancel Button - Second (right side) */}
                            <button
                                onClick={() => setDeletingPage(null)}
                                className="px-6 py-3 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PagesPage;
