'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useNotes } from '@/contexts/NotesContext';
import { socketService } from '@/services/socket';
import {
  Box,
  Container,
  Flex,
  Heading,
  Button,
  useToast,
  IconButton,
  Text,
  VStack,
  HStack,
  useColorModeValue,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Input,
  FormControl,
  FormLabel,
} from '@chakra-ui/react';
import { AddIcon, DeleteIcon } from '@chakra-ui/icons';
import { formatTaiwanTime } from '@/utils/dateFormat';

export default function NotesPage() {
  const router = useRouter();
  const { notes, createNote, deleteNote, refreshNotes } = useNotes();
  const [isCreating, setIsCreating] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newNoteTitle, setNewNoteTitle] = useState('');
  const toast = useToast();

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // 監聽 Socket.IO 更新
  useEffect(() => {
    socketService.connect();
    socketService.onNoteUpdate((data) => {
      console.log("123")
      refreshNotes();
    });

    return () => {
      socketService.offNoteUpdate();
    };
  }, [refreshNotes]);

  const handleCreateNote = async () => {
    try {
      setIsCreating(true);
      const newNote = await createNote(newNoteTitle || '新筆記');

      // 加入筆記的 Socket.IO 房間
      socketService.joinNote(newNote.id);

      // 關閉彈窗並重置標題
      setIsModalOpen(false);
      setNewNoteTitle('');

      router.push(`/notes/${newNote.id}`);
    } catch (error) {
      toast({
        title: '創建筆記失敗',
        description: '請稍後再試',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteNote = async (noteId: string) => {
    try {
      socketService.leaveNote(noteId);
      await deleteNote(noteId);
      toast({
        title: '筆記已刪除',
        status: 'success',
        duration: 2000,
      });
    } catch (error) {
      toast({
        title: '刪除筆記失敗',
        description: '請稍後再試',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleNoteClick = (noteId: string) => {
    socketService.joinNote(noteId);
    router.push(`/notes/${noteId}`);
  };

  return (
    <Container maxW="container.lg" py={8}>
      <Flex mb={6} justify="space-between" align="center">
        <Heading size="lg">我的筆記</Heading>
        <Button
          leftIcon={<AddIcon />}
          colorScheme="blue"
          onClick={() => setIsModalOpen(true)}
          isLoading={isCreating}
        >
          新增筆記
        </Button>
      </Flex>

      <VStack spacing={4} align="stretch">
        {[...notes]
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
          .map((note) => (
          <Box
            key={note.id}
            p={4}
            bg={bgColor}
            borderRadius="lg"
            boxShadow="sm"
            borderWidth={1}
            borderColor={borderColor}
            _hover={{ boxShadow: 'md' }}
            cursor="pointer"
            onClick={() => handleNoteClick(note.id)}
          >
            <Flex justify="space-between" align="center">
              <Box flex={1}>
                <Heading size="md" mb={2}>
                  {note.title}
                </Heading>
                <Text color="gray.500" fontSize="sm">
                  最後更新：{formatTaiwanTime(note.updated_at)}
                </Text>
              </Box>
              <HStack spacing={2}>
                <IconButton
                  aria-label="刪除筆記"
                  icon={<DeleteIcon />}
                  colorScheme="red"
                  variant="ghost"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteNote(note.id);
                  }}
                />
              </HStack>
            </Flex>
          </Box>
        ))}
      </VStack>

      {/* 新增筆記彈窗 */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>新增筆記</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FormControl>
              <FormLabel>筆記標題</FormLabel>
              <Input
                placeholder="請輸入筆記標題"
                value={newNoteTitle}
                onChange={(e) => setNewNoteTitle(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleCreateNote();
                  }
                }}
              />
            </FormControl>
            <Flex mt={4} justify="flex-end">
              <Button
                colorScheme="blue"
                mr={3}
                onClick={handleCreateNote}
                isLoading={isCreating}
              >
                創建
              </Button>
              <Button onClick={() => setIsModalOpen(false)}>取消</Button>
            </Flex>
          </ModalBody>
        </ModalContent>
      </Modal>
    </Container>
  );
} 
