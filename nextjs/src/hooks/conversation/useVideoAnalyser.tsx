import { LINK } from "@/config/config";
import { API_PREFIX } from "@/config/config";
import { STATUS_CODE, TOKEN_PREFIX } from "@/utils/constant";
import { bytesToMegabytes } from "@/utils/common";
import Toast from "@/utils/toast";
import axios from "axios";
import { useState } from "react";
import useConversation from './useConversation';
import { ProAgentCode, ProAgentPythonCode } from "@/types/common";

const useVideoAnalyser = () => {
    const [isLoading, setIsLoading] = useState(false);
    const { getCommonPythonPayload } = useConversation();
    const VIDEO_SIZE_LIMIT = 1000; // IN MB

    const loomVideoAnalysis = async (payload) => {
        try {
            setIsLoading(true);

            const videoResponse = await getVideoUrl(payload.loomUrl);
            if(!videoResponse) return;

            const { companyId, token } = await getCommonPythonPayload();
            const response = await fetch(
                `${LINK.PYTHON_API_URL}${API_PREFIX}/agent/pro-agent/video/upload-gemini-file`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: `${TOKEN_PREFIX}${token}`,
                    },
                    body: JSON.stringify({
                        company_id: companyId,
                        delay_chunk: 0.02,
                        pro_agent_code: ProAgentCode.VIDEO_CALL_ANALYZER,
                        agent_extra_info:{
                            url: payload.loomUrl,
                            cdn_url: videoResponse?.cdnurl,
                            size: videoResponse?.size
                        }                        
                    }),
                }
            );
            
            const jsonResponse = await response.json();
            if (jsonResponse.status === STATUS_CODE.SUCCESS){
                return jsonResponse;
            } else {
                Toast(jsonResponse?.message, 'error');
                return false;
            }
        } catch (error) {
            console.error('Error generating seo topic name', error);
            return null;
        } finally {
            setIsLoading(false);
        }
    }
    
    const getFileSize = async (cdnurl) => {
        try {
            const response = await fetch(cdnurl, {
                method: 'HEAD'
            });

            if(response.ok){
                const contentLength = response.headers.get('Content-Length');
                const fileSizeMB = bytesToMegabytes(contentLength);
                
                return {
                    sizeMb: fileSizeMB,
                    size:contentLength,
                    cdnurl: cdnurl
                };
                
            } else {
                Toast('Failed to get video size details.', 'error');
                return false;
            }  
        } catch (error) {
            return false;
        }
    }

    // Function to get video URL from Loom API
    const getVideoUrl = async (url) => {
        const videoId = extractVideoId(url);
        
        const apiUrl = `https://www.loom.com/api/campaigns/sessions/${videoId}/transcoded-url`;
        
        const headers = {
            //'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            //'Origin': 'https://www.loom.com',
            //'Referer': `https://www.loom.com/share/${videoId}`,
            //'Accept': 'application/json',
        };
        
        try {
            setIsLoading(true);
            const response = await axios.post(apiUrl, {}, { headers });
        
            const data = response.data;
            if (data && data.url) {
                const response = await getFileSize(data?.url);
                if (response && response?.sizeMb > VIDEO_SIZE_LIMIT) {
                    Toast('File size is too large. Please upload a smaller file.', 'error');
                    return;
                }
                return response;
            } else {
                console.log("JSON Response:", data);
            }
        } catch (error) {
            Toast('Invalid Loom Video URL.', 'error');
            return false;
        }
    }

    // Function to extract video ID from Loom URL
    const extractVideoId = (url) => {
        const pattern = /share\/([a-zA-Z0-9]+)/;
        const match = url.match(pattern);
        if (match) {
            return match[1];
        } else {
            Toast("Loom URL not exists", 'error');
            return false;
        }
    }

    return {
        getVideoUrl,
        loomVideoAnalysis,
        isLoading
    }
}

export default useVideoAnalyser;