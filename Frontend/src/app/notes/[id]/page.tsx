'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useNotes } from '@/contexts/NotesContext';
import { socketService } from '@/services/socket';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Box,
  Container,
  Flex,
  Heading,
  Textarea,
  Input,
  Button,
  useToast,
  IconButton,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  useColorModeValue,
  Text,
} from '@chakra-ui/react';
import { ArrowBackIcon } from '@chakra-ui/icons';
import debounce from 'lodash/debounce';

export default function NotePage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const { getNote, updateNote } = useNotes();
  const [note, setNote] = useState<any>(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [isSaving, setIsSaving] = useState(false);
  const toast = useToast();

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // 創建防抖動的更新函數
  const debouncedUpdate = useCallback(
    debounce(async (noteId: string, newTitle: string, newContent: string) => {
      try {
        setIsSaving(true);
        // console.log('發送筆記更新:', { noteId, newTitle, newContent });
        socketService.updateNote(noteId, newContent, newTitle);
        // toast({
        //   title: '已保存',
        //   status: 'success',
        //   duration: 2000,
        //   position: 'bottom-right',
        // });
      } catch (error) {
        console.error('更新失敗:', error);
        toast({
          title: '保存失敗',
          description: '請稍後再試',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
      } finally {
        setIsSaving(false);
      }
    }, 10),
    [toast]
  );

  useEffect(() => {
    if (!params.id) return;

    socketService.connect();
    const loadNote = async () => {
      try {
        const noteData = await getNote(params.id);
        setNote(noteData);
        setTitle(noteData.title);
        setContent(noteData.content);
      } catch (error) {
        console.error('載入筆記失敗:', error);
        toast({
          title: '載入筆記失敗',
          description: '請稍後再試',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
        router.push('/notes');
      }
    };

    loadNote();
    console.log('加入筆記房間:', params.id);
    socketService.joinNote(params.id); // join note room

    socketService.onNoteUpdate((data) => {
      console.log('收到筆記更新:', data);
      // 檢查是否是當前筆記的更新
      if (data.id === params.id) {
        console.log('更新當前筆記:', data);
        setTitle(data.title);
        setContent(data.content);
      }
    });

    return () => {
      console.log('離開筆記房間:', params.id);
      socketService.leaveNote(params.id);
      console.log('移除筆記更新監聽器');
      socketService.offNoteUpdate();
      debouncedUpdate.cancel();
    };
  }, [params.id, getNote, router, toast, debouncedUpdate]);

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTitle = e.target.value;
    setTitle(newTitle);
    debouncedUpdate(params.id, newTitle, content);
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value;
    setContent(newContent);
    debouncedUpdate(params.id, title, newContent);
  };

  if (!note) {
    return null;
  }

  return (
    <Container maxW="container.lg" py={8}>
      <Flex mb={6} align="center">
        <IconButton
          aria-label="返回"
          icon={<ArrowBackIcon />}
          mr={4}
          onClick={() => router.push('/notes')}
        />
        <Heading size="lg">編輯筆記</Heading>
        {isSaving && (
          <Text ml={4} color="gray.500" fontSize="sm">
            保存中...
          </Text>
        )}
      </Flex>

      <Box bg={bgColor} p={6} borderRadius="lg" boxShadow="sm">
        <Input
          value={title}
          onChange={handleTitleChange}
          placeholder="筆記標題"
          size="lg"
          fontSize="2xl"
          fontWeight="bold"
          mb={4}
          variant="unstyled"
        />

        <Tabs index={activeTab} onChange={setActiveTab}>
          <TabList>
            <Tab>編輯</Tab>
            <Tab>預覽</Tab>
          </TabList>

          <TabPanels>
            <TabPanel p={0} mt={4}>
              <Textarea
                value={content}
                onChange={handleContentChange}
                placeholder="開始撰寫筆記...（支援 Markdown 格式）"
                minH="calc(100vh - 300px)"
                fontSize="lg"
                variant="unstyled"
                resize="none"
              />
            </TabPanel>
            <TabPanel p={0} mt={4}>
              <Box
                minH="calc(100vh - 300px)"
                p={4}
                borderWidth={1}
                borderColor={borderColor}
                borderRadius="md"
                overflowY="auto"
              >
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {content}
                </ReactMarkdown>
              </Box>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </Box>
    </Container>
  );
} 
