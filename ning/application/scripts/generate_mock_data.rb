require File.dirname(__FILE__) + "/../db.rb"
Dir.glob(File.join(File.dirname(__FILE__) + "/../models/*.rb")).each do |f| require f end

# Tags
Tag.create(:name => "red", :type => "color")
Tag.create(:name => "green", :type => "color")
Tag.create(:name => "large", :type => "dimensions")
Tag.create(:name => "small", :type => "dimensions")

# Products

# Gucci Handbag
product = Product.create(:name => "Gucci Handbag")
product.medias << Photo.create(
  :url => "http://guccigoods.com/wp-content/uploads/2008/03/authenticate_gucci_handbag.jpg",
  :width => 300,
  :height => 300
)
product.medias << Photo.create(
  :url => "http://allwomenstalk.com/wp-content/uploads/2007/11/gucci41.jpg",
  :width => 400,
  :height => 400
)
product.medias << Video.create(
  :embed_code => '<object width="425" height="344"><param name="movie" value="http://www.youtube.com/v/cD4Bo1pJfSw&hl=en&fs=1&"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/cD4Bo1pJfSw&hl=en&fs=1&" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="425" height="344"></embed></object>',
  :width => "425",
  :height => "344"
)
product.purchase_points << PurchasePoint.create(
  :name => "Gucci Web",
  :address => "www.gucci.com",
  :price => 1000000000.00
) 
product.purchase_points << PurchasePoint.create(
  :name => "Gucci Awesome China Emporium",
  :address => "Beijing, China",
  :price => 10.00
)
product.tags << Tag.first_or_create(:name => "red")
product.tags << Tag.first_or_create(:name => "large")
product.save

# Vuitton handbag
product = Product.create(:name => "Vuitton Handbag")
product.medias << Photo.create(
  :url => "http://www.icantwaittovote.org/blog/images/The%20Louis%20Vuitton%20Mahina%20XXL%20Handbag.jpg",
  :width => 440,
  :height => 304
)
product.medias << Photo.create(
  :url => "http://2.bp.blogspot.com/_4_L4rYWKpoY/R54Brxx6AyI/AAAAAAAAANw/-eIKxxygljQ/s400/Louis_Vuitton_Handbags_LV_Bag.jpg",
  :width => 320,
  :height => 320
)
product.purchase_points << PurchasePoint.create(
  :name => "Vuitton Manhattan",
  :address => "Manhattan, New York, NY",
  :price => 10.00
)
product.tags << Tag.first_or_create(:name => "green")
product.tags << Tag.first_or_create(:name => "small")
product.save