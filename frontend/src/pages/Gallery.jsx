// src/pages/Gallery.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import './Gallery.css';

import result1 from '../assets/results/1.jpg';
import result2 from '../assets/results/2.jpg';
import result3 from '../assets/results/3.jpg';
import result4 from '../assets/results/4.jpg';
import result5 from '../assets/results/5.jpg';
import result6 from '../assets/results/6.jpg';
import result7 from '../assets/results/7.jpg';
import result8 from '../assets/results/8.jpg';

const sampleImages = [result1, result2, result3, result4, result5, result6, result7, result8];

const API_BASE_URL = "http://localhost:8000";

const Gallery = () => {
    const { user, isAuthenticated, loadingAuth } = useAuth();
    const [galleryItems, setGalleryItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (loadingAuth) {
            return;
        }

        const fetchGalleryData = async () => {
            setLoading(true);
            setError(null);

            if (isAuthenticated && user && user.id) {
                console.log("Gallery: User is authenticated. Fetching user-specific ads from backend.");
                try {
                    const response = await axios.get(`${API_BASE_URL}/users/${user.id}`, {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                        }
                    });
                    const fetchedUser = response.data;

                    if (fetchedUser.advertisements && fetchedUser.advertisements.length > 0) {
                        console.log("Gallery: Fetched user advertisements:", fetchedUser.advertisements);
                        const userAdGalleryItems = fetchedUser.advertisements.map(ad => {
                            let imagePath = null;
                            let adCopy = '광고 문구 없음';
                            let adType = '알 수 없음';

                            if (ad.copies && ad.copies.length > 0) {
                                const lastCopy = ad.copies[ad.copies.length - 1];
                                adCopy = lastCopy.copy_text;
                                adType = lastCopy.ad_type;
                            }

                            if (ad.image_preservations && ad.image_preservations.length > 0) {
                                imagePath = ad.image_preservations[ad.image_preservations.length - 1].preserved_image_path;
                            } else if (ad.images && ad.images.length > 0) {
                                imagePath = ad.images[ad.images.length - 1].generated_image_path;
                            }

                            if (imagePath) {
                                return {
                                    id: ad.id,
                                    imageUrl: `${API_BASE_URL}${imagePath}`,
                                    adCopy: adCopy,
                                    adType: adType,
                                };
                            } else {
                                console.warn(`Ad ${ad.id} has no valid image path (neither preserved nor generated).`);
                                return null;
                            }
                        }).filter(item => item !== null);

                        setGalleryItems(userAdGalleryItems);
                    } else {
                        console.log("Gallery: No advertisements found for this user from backend.");
                        setGalleryItems([]);
                    }

                } catch (err) {
                    console.error("갤러리 이미지 로드 오류:", err);
                    setError("이미지를 불러오는 데 실패했습니다.");
                    setGalleryItems([]);
                } finally {
                    setLoading(false);
                }

            } else {
                console.log("Gallery: User not authenticated, displaying sample images.");
                const sampleGalleryItems = sampleImages.map((imagePath, index) => ({
                    id: `sample-${index}`,
                    imageUrl: imagePath,
                    adCopy: `예시 광고 ${index + 1}`,
                    adType: '예시',
                }));
                setGalleryItems(sampleGalleryItems);
                setLoading(false);
                setError(null);
            }
        };

        fetchGalleryData();
    }, [isAuthenticated, user, loadingAuth]);

    if (loading) {
        return (
            <div className="gallery-container">
                <p>갤러리 로드 중...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="gallery-container">
                <p className="error-message">{error}</p>
            </div>
        );
    }

    const renderGalleryContent = () => {
        if (galleryItems.length === 0) {
            return isAuthenticated ? (
                <p>아직 생성된 광고 이미지가 없습니다. 새 광고를 만들어보세요!</p>
            ) : (
                <p>표시할 예시 이미지가 없습니다.</p>
            );
        }

        if (isAuthenticated) {
            return (
                <div className="gallery-grid">
                    {galleryItems.map((item) => (
                        <div key={item.id} className="gallery-card">
                            <img
                                src={item.imageUrl}
                                alt={`Ad for ${item.adType}`}
                                style={{ width: '100%', display: 'block', borderRadius: '8px' }}
                            />
                            <p className="gallery-caption">
                                {item.adCopy}
                                <br />
                                <small>유형: {item.adType}</small>
                            </p>
                        </div>
                    ))}
                </div>
            );
        } else {
            return (
                <div
                    style={{
                        columnCount: 4,      // 컬럼 개수 조절 가능 (3~4 권장)
                        columnGap: '20px',   // 컬럼 사이 간격
                    }}
                >
                    {galleryItems.map((item) => (
                        <div
                            key={item.id}
                            style={{ 
                                breakInside: 'avoid',
                                marginBottom: '20px',
                                background: '#1e1e1e',
                                borderRadius: '12px', 
                                boxShadow: '0 2px 12px rgba(0,0,0,0.3)',
                                padding: '16px',
                                textAlign: 'center',
                            }}
                        >
                            <img
                                src={item.imageUrl}
                                alt={`Ad for ${item.adType}`}
                                style={{ width: '100%', display: 'block', borderRadius: '8px' }}
                            />
                            <p className="gallery-caption">
                                {item.adCopy}
                                <br />
                                <small>유형: {item.adType}</small>
                            </p>
                        </div>
                    ))}
                </div>
            );
        }
    };

    return (
        <div className="gallery-container">
            <h2 className="gallery-title">{isAuthenticated ? '내 광고 갤러리' : '예시 광고 갤러리'}</h2>
            {renderGalleryContent()}
        </div>
    );
};

export default Gallery;
