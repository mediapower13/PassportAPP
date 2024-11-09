const express = require('express');
const router = express.Router();
const mongojs = require('mongojs');
const db = mongojs('passportapp', ['users']);
const bcrypt = require('bcryptjs');
const passport = require('passport');
const { check, validationResult } = require('express-validator');
const LocalStrategy = require('passport-local').Strategy;

// LOGIN PAGE GET
router.get('/login', function(req, res){
  res.render('login');
});

// REGISTER PAGE GET
router.get('/register', function(req, res){
  res.render('register');
});

// REGISTER POST ROUTE
router.post('/register', [
  check('name', 'Name field is required').notEmpty(),
  check('email', 'Email field is required').notEmpty(),
  check('email', 'Please use a valid email address').isEmail(),
  check('username', 'Username field is required').notEmpty(),
  check('password', 'Password field is required').notEmpty(),
  check('password2', 'Passwords do not match').custom((value, { req }) => value === req.body.password)
], function(req, res){
  const errors = validationResult(req);
  
  const { name, email, username, password, password2 } = req.body;

  if (!errors.isEmpty()) {
    console.log('Form has errors.......');
    // Render register view with errors and form data
    res.render('register', {
      errors: errors.array(),
      name,
      email,
      username,
      password,
      password2
    });
  } else {
    // Success handling (you can add database interaction here)

    var newUser = {
      name: name,
      email:email,
      username:username,
      password:password,
      password2:password2,
    }

    bcrypt.genSalt(10, function(err, salt){
      bcrypt.hash(newUser.password, salt, function(err, hash){
        newUser.password = hash;

        db.users.insert(newUser, function(err, doc){
          if(err){
            res.send(err);
          } else {
          console.log('user Added........');
    
    
          //sucess message
          req.flash('sucess', 'You are registered and can now log in');
    
          res.location('/');
          res.redirect('/');
          }
        });

      });
    });
    
   

    // Example: You can now hash the password and store the user in the database
    bcrypt.genSalt(10, (err, salt) => {
      bcrypt.hash(password, salt, (err, hash) => {
        if (err) throw err;

        // Insert user into the database with hashed password
        db.users.insert({ name, email, username, password: hash }, (err, user) => {
          if (err) {
            console.error(err);
            res.status(500).send('Database error');
          } else {
            res.send('Registration successful');
          }
        });
      });
    });
  }
});

passport.serializeUser(function(user, done){
  done(null, user._id);
});

passport.deserializeUser(function(id, done) {
 db.users.findOne({_id: mongojs.ObjectID(id)}, function(err, user) {
      done(err,user);
  });
});

passport.use(new LocalStrategy(
  function(username, password, done){
     db.users.findOne({username: username}, function(err, user){
      if(err) {
        return done(err);
      }
      if(!user){
        return done(null, false, {message: 'Incorrect username'});
      }

      bcrypt.compare(password, user.password, function(err, isMatch){
        if(err) {
          return done(err);
        }

        if(isMatch) {
          return done(null, user);
        } else {
          return done(null, false, {message: 'Incorrect password'});
        }
      });
      
     });
  }
));

router.post('/login',
   passport.authenticate('local', { successRedirect: '/',
                                    failureRedirect: '/users/login',
                                    failureFlash: 'Invalid username or password' }),
                                    
  function(req, res){
    console.log('Auth successfull');  
    res.redirect('/');
                                    

  });

  router.get('/logout', function(res, res){
    req.logout();
    req.flash('sucess', 'You have logged out');
    res.redirect('/users/login');
  })

module.exports = router;
