import React, { useEffect, useState } from 'react'
import { Badge, Col, Container, Form, Image, Row, Spinner } from 'react-bootstrap'
import { useParams, Link } from 'react-router-dom'
import Apis, { endpoints } from '../configs/Apis'
import Header from '../layouts/Header';
import Footer from '../layouts/Footer';
import Moment from 'react-moment';
import { Button } from 'bootstrap';
import { useSelector } from 'react-redux';
import cookies from 'react-cookies';
import Rating from 'react-rating';
import 'boxicons';




export default function PostDetail() {
    const [post, setPost] = useState(null)
    let { postId } = useParams()
    const [comments, setComments] = useState([])
    const [commentContent, setCommentContent] = useState(null)
    const [rating, setRating] = useState(0)
    const [changed, setChanged] = useState(1)
    let user = useSelector(state => state.user.user)
  


    useEffect(() => {
      let loadPostDetail = async () => {
        try {
            let res = await Apis.get(endpoints['post-detail'](postId), {
                headers: {
                  'Authorization': `Bearer ${cookies.load('access_token')}`
                }
            })
            
            setPost(res.data)
            setRating(res.data.rate)
        } catch (err) {
            console.error(err)
        }
      }
      let loadComments = async () => {
        try {
            let res = await Apis.get(endpoints['comments'](postId), {
              headers: {
                'Authorization': `Bearer ${cookies.load('access_token')}`
              }
            })
            setComments(res.data)
            console.info(res.data)
        }
        catch(err) {
            console.error(err)
          }
      }
        
      loadComments()
      loadPostDetail()
      
    }, [changed])

  const addComment = async (event) => {
    event.preventDefault()

    let loadPostDetail = async () => {
      try {
          let res = await Apis.get(endpoints['post-detail'](postId))
          
          setPost(res.data)
      } catch (err) {
          console.error(err)
      }
    }
    
    try {
        let res = await Apis.post(endpoints['add-comment'](postId), {
            'content': commentContent
        }, {
          headers: {
            'Authorization': `Bearer ${cookies.load('access_token')}`
          }
        })

        console.info(res.data)
        comments.push(res.data)
        setComments(comments)
        setChanged(comments.length)
    } catch (err) {
      console.error(err)
    }
  }

  const saveRating = async (rate) => {
      if (window.confirm('Ban muon danh gia bai hoc nay?') == true) {
        try {
            let res = await Apis.post(endpoints['rating'](postId), {
              'rating': rate
            }, {
              headers: {
                'Authorization': `Bearer ${cookies.load('access_token')}`
              }
            })
            console.info(res.data)
        } catch (err) {
          console.error(err)
        }
      }
  }

  if (post === null)
    return <Spinner animation='border'/>
  
  let comment = <em><Link to='/login'> Đăng nhập </Link> để hình luận </em>
  let r = ""
  let avt =""
  if (user !== null && user !== undefined) {
      comment =  <Form onSubmit={addComment}>
                    <Form.Group className="mb-3" controlId="comentContent">
                      <Form.Control as="textarea"
                                    value={commentContent}
                                    onChange={(event) => setCommentContent(event.target.value)}
                                    placeholder='Nhập nội dung bình luận' rows={3} />
                    </Form.Group>
                    <button type='submit'>Thêm bình luận</button>
                </Form>
      r = <Rating initialRating={rating}
                  onClick={saveRating}
                  emptySymbol="fa fa-star-o fa-2x"
                  fullSymbol="fa fa-star fa-2x"
                />
      avt =  <Image src={ user.avatar} alt="" style={{'height': '70px', 'width': '70px'}} />
  }

  return (
    <>
    <Header />
    <div style={{'background': '#f4f2f2'}}>
    <Container>
      <h1 className='text-success'>PostDetail</h1>
      <Row>
            <Col md={4} xs={12}>
              <Image src={post.image} style={{width:'417px', height: '557px'}} rounded fluid />
            </Col>
            <Col md={8} xs={12}>
              <h2>{post.title}</h2>
              <p>Ngày tạo: {post.created_date}</p>
              <p>Ngày cập nhật: {post.updated_date}</p>
              <p>
                  {post.tags.map(t => <Badge bg='secondary'>{t.name}</Badge>)}
              </p>
              <p>
                {r}
              </p>
              
            </Col>
        </Row>
        <hr />
        <div>
           {post.content}
        </div>
        {comments.map(c => 
               <div className="coment-area" >
               <ul className="we-comet">
                   <li>
                       <div className="comet-avatar">
                          {avt}
                       </div>
                       <div className="we-comment">
                           <div className="coment-head">
                               <h5><a  title="">{c.creator.username}</a></h5>
                               <span> <Moment fromNow>{c.created_date}</Moment> </span>
                               <a className="we-reply" title="Reply"><i className="fa fa-reply"></i></a>
                           </div>
                           <p>{c.content}</p>
                       </div>
                      
                   </li>
                   
               </ul>
           </div>
          
          )}
        {comment}
        <br></br>
        </Container>
        </div>
        <Footer/>
    </>
  )
}
